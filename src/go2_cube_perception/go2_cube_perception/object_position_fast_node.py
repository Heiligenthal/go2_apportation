"""FAST 3D-position skeleton from bbox + depth + intrinsics."""

from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple

from . import frames, topics
from .contracts import DEFAULT_CONTRACTS
from .depth_roi import BoundingBox2D, CameraIntrinsics, DepthRoiConfig, DepthRoiSummary, summarize_depth_bbox
from .object_detector_trt_node import Detector2DCandidate
from .msg_adapters import (
    InternalFastDetectionCandidate,
    InternalMapFastMeasurement,
    build_detections3d_fast_msg,
)

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.time import Time
    from go2_apportation_msgs.msg import Detection3DArray
    from tf2_ros import Buffer, TransformListener
except ImportError:  # pragma: no cover
    rclpy = None
    Node = object  # type: ignore[assignment]
    Time = None  # type: ignore[assignment]
    Detection3DArray = None  # type: ignore[assignment]
    Buffer = None  # type: ignore[assignment]
    TransformListener = None  # type: ignore[assignment]


@dataclass(frozen=True)
class FastPositionEstimate:
    """Owner-local fast position estimate."""

    frame_id: str
    center_xyz: Tuple[float, float, float]
    depth_m: float
    confidence: float
    depth_summary: DepthRoiSummary
    pixel_center_uv: Tuple[float, float]


@dataclass(frozen=True)
class FastPipelineOutputs:
    """Owner-local FAST outputs for public and internal consumers."""

    public_detection: Optional[InternalFastDetectionCandidate]
    map_measurement: Optional[InternalMapFastMeasurement]


@dataclass(frozen=True)
class FastProjectionConfig:
    """Runtime-safe FAST projection settings."""

    output_frame: str
    min_depth_m: float
    max_depth_m: float
    min_valid_pixels: int
    trim_ratio: float
    allow_frame_passthrough_if_no_tf: bool = False
    map_tracking_frame: str = frames.INTERNAL_TRACKING_FRAME


@dataclass(frozen=True)
class FastRuntimeSnapshot:
    """Bag-/runtime-friendly readiness snapshot for FAST projection."""

    candidate_topic: str
    depth_topic: str
    camera_info_topic: str
    candidate_ready: bool
    depth_ready: bool
    intrinsics_ready: bool
    can_project: bool
    map_tf_ready: bool


TransformPointToMap = Callable[[Tuple[float, float, float], str, float], Optional[Tuple[float, float, float]]]


def resolve_fast_output_frame(source_frame_id: str, output_frame: str, allow_passthrough: bool) -> Optional[str]:
    """Choose an output frame without silently inventing TF availability.

    The runtime TF chain is consumed from bringup/H1. This owner package does
    not publish fallback TF or a second camera frame path.
    """

    if not output_frame:
        return source_frame_id or None
    if source_frame_id == output_frame:
        return output_frame
    if source_frame_id and allow_passthrough:
        return source_frame_id
    return None


def build_internal_map_measurement(
    estimate: FastPositionEstimate,
    *,
    candidate: Detector2DCandidate,
    transform_point_to_map: Optional[TransformPointToMap],
    map_frame: str,
) -> Optional[InternalMapFastMeasurement]:
    """Transform a sensor-frame FAST estimate into the owner-local map frame."""

    if estimate.frame_id == map_frame:
        position_map_xyz = estimate.center_xyz
    elif transform_point_to_map is None:
        return None
    else:
        position_map_xyz = transform_point_to_map(
            estimate.center_xyz,
            estimate.frame_id,
            float(candidate.stamp_s),
        )
    if position_map_xyz is None:
        return None
    return InternalMapFastMeasurement(
        frame_id=map_frame,
        position_map_xyz=position_map_xyz,
        measurement_confidence=float(candidate.confidence),
        stamp_s=float(candidate.stamp_s),
        source_frame=estimate.frame_id,
        bbox_center_norm_xy=tuple(float(value) for value in candidate.bbox_center_norm_xy),
        centered=bool(candidate.centered),
    )


def evaluate_fast_runtime_snapshot(
    *,
    now_s: float,
    candidate_stamp_s: Optional[float],
    depth_stamp_s: Optional[float],
    intrinsics_stamp_s: Optional[float],
    freshness_timeout_s: float,
    candidate_topic: str,
    depth_topic: str,
    camera_info_topic: str,
    map_tf_ready: bool,
) -> FastRuntimeSnapshot:
    """Summarize FAST readiness without depending on ROS subscriptions."""

    def is_fresh(stamp_s: Optional[float]) -> bool:
        if stamp_s is None:
            return False
        return max(0.0, now_s - float(stamp_s)) <= freshness_timeout_s

    candidate_ready = is_fresh(candidate_stamp_s)
    depth_ready = is_fresh(depth_stamp_s)
    intrinsics_ready = is_fresh(intrinsics_stamp_s)
    return FastRuntimeSnapshot(
        candidate_topic=candidate_topic,
        depth_topic=depth_topic,
        camera_info_topic=camera_info_topic,
        candidate_ready=candidate_ready,
        depth_ready=depth_ready,
        intrinsics_ready=intrinsics_ready,
        can_project=candidate_ready and depth_ready and intrinsics_ready,
        map_tf_ready=bool(map_tf_ready),
    )


def project_candidate_to_fast_estimate(
    candidate: Detector2DCandidate,
    depth_image,
    intrinsics: CameraIntrinsics,
    config: FastProjectionConfig,
) -> Optional[FastPositionEstimate]:
    """Project a 2D candidate into a 3D center estimate with depth gating."""

    frame_id = resolve_fast_output_frame(
        source_frame_id=candidate.frame_id,
        output_frame=config.output_frame,
        allow_passthrough=config.allow_frame_passthrough_if_no_tf,
    )
    if frame_id is None:
        return None

    depth_summary = summarize_depth_bbox(
        depth_image,
        bbox=candidate.bbox,
        config=DepthRoiConfig(
            min_depth_m=config.min_depth_m,
            max_depth_m=config.max_depth_m,
            min_valid_pixels=config.min_valid_pixels,
            trim_ratio=config.trim_ratio,
        ),
    )
    if depth_summary is None:
        return None

    u = candidate.bbox.center_u
    v = candidate.bbox.center_v
    z = depth_summary.depth_m
    x = ((u - intrinsics.cx) * z) / intrinsics.fx
    y = ((v - intrinsics.cy) * z) / intrinsics.fy
    return FastPositionEstimate(
        frame_id=frame_id,
        center_xyz=(x, y, z),
        depth_m=z,
        confidence=float(candidate.confidence),
        depth_summary=depth_summary,
        pixel_center_uv=(u, v),
    )


def build_public_fast_detection(
    candidate: Detector2DCandidate,
    depth_image,
    intrinsics: CameraIntrinsics,
    config: FastProjectionConfig,
) -> Optional[InternalFastDetectionCandidate]:
    """Convert a 2D candidate into the READY public Detection3DArray payload."""

    estimate = project_candidate_to_fast_estimate(
        candidate=candidate,
        depth_image=depth_image,
        intrinsics=intrinsics,
        config=config,
    )
    if estimate is None:
        return None
    return InternalFastDetectionCandidate(
        frame_id=estimate.frame_id,
        center_xyz=estimate.center_xyz,
        confidence=estimate.confidence,
        source_hint=candidate.source_hint,
        stamp_s=candidate.stamp_s,
        class_id=candidate.class_id,
    )


def build_fast_pipeline_outputs(
    candidate: Detector2DCandidate,
    depth_image,
    intrinsics: CameraIntrinsics,
    config: FastProjectionConfig,
    *,
    transform_point_to_map: Optional[TransformPointToMap] = None,
) -> FastPipelineOutputs:
    """Build owner-local map measurement plus conservative public FAST output."""

    sensor_config = FastProjectionConfig(
        output_frame=candidate.frame_id or "",
        min_depth_m=config.min_depth_m,
        max_depth_m=config.max_depth_m,
        min_valid_pixels=config.min_valid_pixels,
        trim_ratio=config.trim_ratio,
        allow_frame_passthrough_if_no_tf=True,
        map_tracking_frame=config.map_tracking_frame,
    )
    sensor_estimate = project_candidate_to_fast_estimate(
        candidate=candidate,
        depth_image=depth_image,
        intrinsics=intrinsics,
        config=sensor_config,
    )
    public_detection = build_public_fast_detection(
        candidate=candidate,
        depth_image=depth_image,
        intrinsics=intrinsics,
        config=config,
    )
    map_measurement = None
    if sensor_estimate is not None:
        map_measurement = build_internal_map_measurement(
            sensor_estimate,
            candidate=candidate,
            transform_point_to_map=transform_point_to_map,
            map_frame=config.map_tracking_frame,
        )
    return FastPipelineOutputs(
        public_detection=public_detection,
        map_measurement=map_measurement,
    )


class ObjectPositionFastNode(Node):
    """FAST path skeleton with READY public Detection3DArray output."""

    def __init__(self) -> None:
        super().__init__("object_position_fast_node")
        self.declare_parameter("enabled", False)
        self.declare_parameter("position_rate_hz", 30.0)
        self.declare_parameter("depth_min_m", 0.45)
        self.declare_parameter("depth_max_m", 3.5)
        self.declare_parameter("depth_min_valid_pixels", 8)
        self.declare_parameter("depth_trim_ratio", 0.1)
        self.declare_parameter("output_mode", "public_detection3d_array")
        self.declare_parameter("output_frame", DEFAULT_CONTRACTS.fast_output_frame)
        self.declare_parameter("map_tracking_frame", DEFAULT_CONTRACTS.internal_tracking_frame)
        self.declare_parameter("allow_frame_passthrough_if_no_tf", False)
        self.declare_parameter("rgb_bbox_topic", topics.INTERNAL_CUBE_BBOX)
        self.declare_parameter("depth_topic", topics.DEPTH_IMAGE)
        self.declare_parameter("camera_info_topic", topics.CAMERA_INFO)
        self.declare_parameter("internal_fast_candidate_topic", topics.INTERNAL_FAST_CANDIDATE)
        self.declare_parameter("internal_map_measurement_topic", topics.INTERNAL_MAP_MEASUREMENT)
        self.declare_parameter("input_freshness_timeout_s", 0.5)
        self.declare_parameter("ingest_mode", "owner_local_candidate")
        self.declare_parameter("enable_tf_map_lookup", True)
        self.declare_parameter("map_transform_timeout_s", 0.05)
        self.declare_parameter("detections3d_fast_topic", DEFAULT_CONTRACTS.detections3d_fast_topic)
        self._detections_publisher = None
        self._latest_candidate: Optional[Detector2DCandidate] = None
        self._latest_depth_image = None
        self._latest_intrinsics: Optional[CameraIntrinsics] = None
        self._latest_candidate_stamp_s: Optional[float] = None
        self._latest_depth_stamp_s: Optional[float] = None
        self._latest_intrinsics_stamp_s: Optional[float] = None
        self._latest_map_measurement: Optional[InternalMapFastMeasurement] = None
        self._tf_buffer = Buffer() if Buffer is not None else None
        self._tf_listener = (
            TransformListener(self._tf_buffer, self) if self._tf_buffer is not None and TransformListener is not None else None
        )
        self._map_transform_provider: Optional[TransformPointToMap] = None
        if Detection3DArray is not None:
            self._detections_publisher = self.create_publisher(
                Detection3DArray,
                str(self.get_parameter("detections3d_fast_topic").value),
                10,
            )
        self._timer = self.create_timer(1.0 / max(self.position_rate_hz, 1.0), self._tick)

    @property
    def position_rate_hz(self) -> float:
        return float(self.get_parameter("position_rate_hz").value)

    def projection_config(self) -> FastProjectionConfig:
        """Expose the active projection settings for tests and diagnostics."""

        return FastProjectionConfig(
            output_frame=str(self.get_parameter("output_frame").value),
            min_depth_m=float(self.get_parameter("depth_min_m").value),
            max_depth_m=float(self.get_parameter("depth_max_m").value),
            min_valid_pixels=int(self.get_parameter("depth_min_valid_pixels").value),
            trim_ratio=float(self.get_parameter("depth_trim_ratio").value),
            allow_frame_passthrough_if_no_tf=bool(
                self.get_parameter("allow_frame_passthrough_if_no_tf").value
            ),
            map_tracking_frame=str(self.get_parameter("map_tracking_frame").value),
        )

    def ingest_candidate(self, candidate: Detector2DCandidate) -> None:
        """Owner-local hook for detector output or offline replay injection."""

        self._latest_candidate = candidate
        self._latest_candidate_stamp_s = float(candidate.stamp_s)

    def ingest_depth_image(self, depth_image, stamp_s: Optional[float] = None) -> None:
        """Owner-local hook for aligned depth input or offline replay injection."""

        self._latest_depth_image = depth_image
        if stamp_s is not None:
            self._latest_depth_stamp_s = float(stamp_s)

    def ingest_intrinsics(self, intrinsics: CameraIntrinsics, stamp_s: Optional[float] = None) -> None:
        """Owner-local hook for camera intrinsics or bag replay scaffolding."""

        self._latest_intrinsics = intrinsics
        if stamp_s is not None:
            self._latest_intrinsics_stamp_s = float(stamp_s)

    def set_map_transform_provider_for_testing(
        self,
        provider: Optional[TransformPointToMap],
    ) -> None:
        """Inject a TF consumer for tests without taking TF ownership."""

        self._map_transform_provider = provider

    def latest_map_measurement(self) -> Optional[InternalMapFastMeasurement]:
        """Expose the freshest owner-local map measurement for tests/owner chaining."""

        return self._latest_map_measurement

    def _transform_point_to_map(
        self,
        point_xyz: Tuple[float, float, float],
        source_frame_id: str,
        stamp_s: float,
    ) -> Optional[Tuple[float, float, float]]:
        if not bool(self.get_parameter("enable_tf_map_lookup").value):
            return None
        if self._map_transform_provider is not None:
            return self._map_transform_provider(point_xyz, source_frame_id, stamp_s)
        if self._tf_buffer is None or not source_frame_id:
            return None
        try:
            transform = self._tf_buffer.lookup_transform(
                str(self.get_parameter("map_tracking_frame").value),
                source_frame_id,
                Time(seconds=max(0.0, float(stamp_s))) if Time is not None else None,
            )
        except Exception:  # pragma: no cover - exercised through provider tests.
            return None
        tx = float(transform.transform.translation.x)
        ty = float(transform.transform.translation.y)
        tz = float(transform.transform.translation.z)
        return (
            float(point_xyz[0]) + tx,
            float(point_xyz[1]) + ty,
            float(point_xyz[2]) + tz,
        )

    def runtime_snapshot(self, now_s: float) -> FastRuntimeSnapshot:
        """Expose FAST runtime readiness for bag/replay tests and diagnostics."""

        return evaluate_fast_runtime_snapshot(
            now_s=now_s,
            candidate_stamp_s=self._latest_candidate_stamp_s,
            depth_stamp_s=self._latest_depth_stamp_s,
            intrinsics_stamp_s=self._latest_intrinsics_stamp_s,
            freshness_timeout_s=float(self.get_parameter("input_freshness_timeout_s").value),
            candidate_topic=str(self.get_parameter("rgb_bbox_topic").value),
            depth_topic=str(self.get_parameter("depth_topic").value),
            camera_info_topic=str(self.get_parameter("camera_info_topic").value),
            map_tf_ready=bool(self.get_parameter("enable_tf_map_lookup").value),
        )

    def _tick(self) -> None:
        if not bool(self.get_parameter("enabled").value):
            return

        now_s = 0.0
        if rclpy is not None:
            now_s = self.get_clock().now().nanoseconds / 1_000_000_000.0
        snapshot = self.runtime_snapshot(now_s=now_s)
        if not snapshot.can_project or self._latest_candidate is None or self._latest_depth_image is None or self._latest_intrinsics is None:
            self.get_logger().debug("FAST projection waiting for candidate, depth image, and camera intrinsics.")
            return

        outputs = build_fast_pipeline_outputs(
            self._latest_candidate,
            depth_image=self._latest_depth_image,
            intrinsics=self._latest_intrinsics,
            config=self.projection_config(),
            transform_point_to_map=self._transform_point_to_map,
        )
        self._latest_map_measurement = outputs.map_measurement
        if outputs.public_detection is None:
            self.get_logger().warn(
                "FAST projection skipped publish because depth was insufficient or frame handoff was unsafe."
            )
            return
        if self._detections_publisher is None:
            self.get_logger().warn("go2_apportation_msgs/Detection3DArray not available; skipping publish.")
            return

        self._detections_publisher.publish(build_detections3d_fast_msg(outputs.public_detection))


def main(args: Optional[Sequence[str]] = None) -> int:
    """Run the ROS node when rclpy is available."""

    if rclpy is None:
        raise RuntimeError("rclpy is required to run object_position_fast_node")
    rclpy.init(args=args)
    node = ObjectPositionFastNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0
