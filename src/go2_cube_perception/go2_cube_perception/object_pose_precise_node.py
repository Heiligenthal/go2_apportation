"""PRECISE cube pose skeleton for grasp-relevant object pose."""

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from .contracts import DEFAULT_CONTRACTS
from .cube_grasp_pose import (
    CubeGraspEstimatorConfig,
    CubeGraspPose,
    estimate_cube_grasp_pose,
)
from .depth_roi import BoundingBox2D, CameraIntrinsics, PointCloudExtractionConfig, extract_local_point_cloud
from .msg_adapters import (
    InternalPrecisePoseCandidate,
    build_object_last_seen_msg,
    build_object_pose_msg,
)

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped
    from rclpy.duration import Duration
    from tf2_ros import Buffer, TransformException, TransformListener
except ImportError:  # pragma: no cover
    rclpy = None
    Node = object  # type: ignore[assignment]
    PoseStamped = None  # type: ignore[assignment]
    Duration = None  # type: ignore[assignment]
    Buffer = None  # type: ignore[assignment]
    TransformException = Exception  # type: ignore[assignment]
    TransformListener = None  # type: ignore[assignment]


@dataclass(frozen=True)
class PrecisePoseEstimate:
    """Owner-local precise pose estimate."""

    grasp_pose: CubeGraspPose
    confidence: float
    point_count: int


@dataclass(frozen=True)
class PreciseRoiCandidate:
    """Owner-local PRECISE candidate, ready for future segmentation backend hookup."""

    bbox: BoundingBox2D
    confidence: float
    frame_id: str
    stamp_s: float = 0.0
    support_mask: Optional[Sequence[Sequence[bool]]] = None
    source_hint: str = "precise_candidate"


@dataclass(frozen=True)
class PrecisePoseComputationConfig:
    """Defensive PRECISE settings for depth support and cube plausibility."""

    output_pose_frame: str
    last_seen_frame: str
    cube_edge_length_m: float
    min_depth_m: float
    max_depth_m: float
    min_valid_points: int
    max_depth_deviation_m: float
    max_axis_aligned_extent_m: float
    min_in_plane_span_m: float
    max_in_plane_span_m: float
    max_face_thickness_m: float


@dataclass(frozen=True)
class PrecisePublishDecision:
    """Conservative public publish decisions for PRECISE outputs."""

    publish_pose: bool
    publish_last_seen: bool


@dataclass(frozen=True)
class PreciseRuntimeSnapshot:
    """Bag-/runtime-friendly readiness snapshot for PRECISE geometry."""

    candidate_topic: str
    depth_topic: str
    camera_info_topic: str
    rgb_topic: str
    candidate_ready: bool
    depth_ready: bool
    intrinsics_ready: bool
    can_estimate_pose: bool


@dataclass(frozen=True)
class RigidTransform:
    """Simple rigid transform for defensive last_seen frame handoff."""

    target_frame: str
    translation_xyz: Tuple[float, float, float]
    rotation_xyzw: Tuple[float, float, float, float]


def resolve_precise_output_frame(source_frame_id: str, output_frame: str) -> Optional[str]:
    """Only accept public pose publication when the frame handoff is already exact.

    The runtime TF chain is consumed from bringup/H1. This owner package does
    not create fallback TF or publish an additional camera_link path.
    """

    if not output_frame:
        return source_frame_id or None
    if source_frame_id == output_frame:
        return output_frame
    return None


def evaluate_precise_runtime_snapshot(
    *,
    now_s: float,
    candidate_stamp_s: Optional[float],
    depth_stamp_s: Optional[float],
    intrinsics_stamp_s: Optional[float],
    freshness_timeout_s: float,
    candidate_topic: str,
    depth_topic: str,
    camera_info_topic: str,
    rgb_topic: str,
) -> PreciseRuntimeSnapshot:
    """Summarize PRECISE readiness without depending on ROS subscriptions."""

    def is_fresh(stamp_s: Optional[float]) -> bool:
        if stamp_s is None:
            return False
        return max(0.0, now_s - float(stamp_s)) <= freshness_timeout_s

    candidate_ready = is_fresh(candidate_stamp_s)
    depth_ready = is_fresh(depth_stamp_s)
    intrinsics_ready = is_fresh(intrinsics_stamp_s)
    return PreciseRuntimeSnapshot(
        candidate_topic=candidate_topic,
        depth_topic=depth_topic,
        camera_info_topic=camera_info_topic,
        rgb_topic=rgb_topic,
        candidate_ready=candidate_ready,
        depth_ready=depth_ready,
        intrinsics_ready=intrinsics_ready,
        can_estimate_pose=candidate_ready and depth_ready and intrinsics_ready,
    )


def _quaternion_multiply(
    a: Tuple[float, float, float, float],
    b: Tuple[float, float, float, float],
) -> Tuple[float, float, float, float]:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _rotate_vector(
    rotation_xyzw: Tuple[float, float, float, float],
    vector_xyz: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    qx, qy, qz, qw = rotation_xyzw
    vx, vy, vz = vector_xyz
    uv = (
        qy * vz - qz * vy,
        qz * vx - qx * vz,
        qx * vy - qy * vx,
    )
    uuv = (
        qy * uv[2] - qz * uv[1],
        qz * uv[0] - qx * uv[2],
        qx * uv[1] - qy * uv[0],
    )
    return (
        vx + 2.0 * (qw * uv[0] + uuv[0]),
        vy + 2.0 * (qw * uv[1] + uuv[1]),
        vz + 2.0 * (qw * uv[2] + uuv[2]),
    )


def transform_precise_candidate(
    candidate: InternalPrecisePoseCandidate,
    transform: RigidTransform,
) -> InternalPrecisePoseCandidate:
    """Apply a rigid transform without faking frame identity."""

    rotated_center = _rotate_vector(transform.rotation_xyzw, candidate.center_xyz)
    transformed_center = (
        rotated_center[0] + transform.translation_xyz[0],
        rotated_center[1] + transform.translation_xyz[1],
        rotated_center[2] + transform.translation_xyz[2],
    )
    transformed_normal = _rotate_vector(transform.rotation_xyzw, candidate.face_normal)
    transformed_axis = _rotate_vector(transform.rotation_xyzw, candidate.edge_axis_mod_pi)
    transformed_orientation = _quaternion_multiply(transform.rotation_xyzw, candidate.orientation_xyzw)
    return InternalPrecisePoseCandidate(
        frame_id=transform.target_frame,
        center_xyz=transformed_center,
        face_normal=transformed_normal,
        edge_axis_mod_pi=transformed_axis,
        confidence=candidate.confidence,
        orientation_xyzw=transformed_orientation,
        stamp_s=candidate.stamp_s,
    )


def resolve_last_seen_candidate(
    candidate: InternalPrecisePoseCandidate,
    *,
    last_seen_frame: str,
    transform_provider=None,
) -> Optional[InternalPrecisePoseCandidate]:
    """Return a map-ready last_seen candidate only if frame handoff is trustworthy."""

    if candidate.frame_id == last_seen_frame:
        return candidate
    if transform_provider is None:
        return None
    transform = transform_provider(candidate.frame_id, last_seen_frame, candidate.stamp_s)
    if transform is None:
        return None
    return transform_precise_candidate(candidate, transform)


def estimate_precise_pose_from_candidate(
    candidate: PreciseRoiCandidate,
    *,
    depth_image,
    intrinsics: CameraIntrinsics,
    config: PrecisePoseComputationConfig,
) -> Optional[PrecisePoseEstimate]:
    """Estimate a conservative grasp pose from local depth support only."""

    output_frame = resolve_precise_output_frame(candidate.frame_id, config.output_pose_frame)
    if output_frame is None:
        return None

    point_cloud = extract_local_point_cloud(
        depth_image,
        bbox=candidate.bbox,
        intrinsics=intrinsics,
        config=PointCloudExtractionConfig(
            min_depth_m=config.min_depth_m,
            max_depth_m=config.max_depth_m,
            min_valid_points=config.min_valid_points,
            max_depth_deviation_m=config.max_depth_deviation_m,
            max_axis_aligned_extent_m=config.max_axis_aligned_extent_m,
        ),
        support_mask=candidate.support_mask,
    )
    if point_cloud is None:
        return None

    grasp_estimate = estimate_cube_grasp_pose(
        point_cloud.points_xyz,
        source_frame=output_frame,
        config=CubeGraspEstimatorConfig(
            cube_edge_length_m=config.cube_edge_length_m,
            min_valid_points=config.min_valid_points,
            min_in_plane_span_m=config.min_in_plane_span_m,
            max_in_plane_span_m=config.max_in_plane_span_m,
            max_face_thickness_m=config.max_face_thickness_m,
        ),
    )
    if grasp_estimate is None:
        return None

    return PrecisePoseEstimate(
        grasp_pose=grasp_estimate.grasp_pose,
        confidence=candidate.confidence,
        point_count=grasp_estimate.diagnostics.point_count,
    )


def build_internal_precise_pose_candidate(
    estimate: PrecisePoseEstimate,
    *,
    stamp_s: float,
) -> InternalPrecisePoseCandidate:
    """Bridge the local PRECISE estimate onto the READY public pose builders."""

    return InternalPrecisePoseCandidate(
        frame_id=estimate.grasp_pose.source_frame,
        center_xyz=estimate.grasp_pose.center_xyz,
        face_normal=estimate.grasp_pose.face_normal,
        edge_axis_mod_pi=estimate.grasp_pose.edge_axis_mod_pi,
        confidence=estimate.confidence,
        orientation_xyzw=estimate.grasp_pose.orientation_xyzw(),
        stamp_s=stamp_s,
    )


def decide_precise_publication(
    estimate: Optional[PrecisePoseEstimate],
    *,
    last_seen_frame: str,
) -> PrecisePublishDecision:
    """Publish last_seen only when the PRECISE pose already lives in the required frame."""

    if estimate is None:
        return PrecisePublishDecision(publish_pose=False, publish_last_seen=False)
    publish_pose = True
    publish_last_seen = estimate.grasp_pose.source_frame == last_seen_frame
    return PrecisePublishDecision(
        publish_pose=publish_pose,
        publish_last_seen=publish_last_seen,
    )


class ObjectPosePreciseNode(Node):
    """PRECISE path skeleton with READY public PoseStamped outputs."""

    def __init__(self) -> None:
        super().__init__("object_pose_precise_node")
        self.declare_parameter("enabled", False)
        self.declare_parameter("precise_rate_hz", 5.0)
        self.declare_parameter("canonicalize_mod_pi", True)
        self.declare_parameter("output_pose_frame", DEFAULT_CONTRACTS.precise_output_frame)
        self.declare_parameter("object_pose_topic", DEFAULT_CONTRACTS.object_pose_topic)
        self.declare_parameter("object_last_seen_topic", DEFAULT_CONTRACTS.object_last_seen_topic)
        self.declare_parameter("object_last_seen_frame", DEFAULT_CONTRACTS.last_seen_output_frame)
        self.declare_parameter("depth_min_m", 0.45)
        self.declare_parameter("depth_max_m", 3.5)
        self.declare_parameter("rgb_topic", "/camera/realsense2_camera/color/image_raw")
        self.declare_parameter("depth_topic", "/camera/realsense2_camera/aligned_depth_to_color/image_raw")
        self.declare_parameter("camera_info_topic", "/camera/realsense2_camera/color/camera_info")
        self.declare_parameter("internal_precise_candidate_topic", "/perception/internal/cube_pose_candidate")
        self.declare_parameter("input_freshness_timeout_s", 0.5)
        self.declare_parameter("ingest_mode", "owner_local_candidate")
        self.declare_parameter("enable_tf_last_seen_lookup", True)
        self.declare_parameter("last_seen_transform_timeout_s", 0.05)
        self.declare_parameter("min_valid_points", 24)
        self.declare_parameter("max_depth_deviation_m", 0.03)
        self.declare_parameter("max_axis_aligned_extent_m", 0.12)
        self.declare_parameter("min_in_plane_span_m", 0.01)
        self.declare_parameter("max_in_plane_span_m", 0.09)
        self.declare_parameter("max_face_thickness_m", 0.02)
        self.declare_parameter("segmentation_engine_path", "")
        self._object_pose_publisher = None
        self._object_last_seen_publisher = None
        self._latest_candidate: Optional[PreciseRoiCandidate] = None
        self._latest_depth_image = None
        self._latest_intrinsics: Optional[CameraIntrinsics] = None
        self._latest_candidate_stamp_s: Optional[float] = None
        self._latest_depth_stamp_s: Optional[float] = None
        self._latest_intrinsics_stamp_s: Optional[float] = None
        self._tf_buffer = None
        self._tf_listener = None
        if Buffer is not None and TransformListener is not None and bool(
            self.get_parameter("enable_tf_last_seen_lookup").value
        ):
            self._tf_buffer = Buffer()
            self._tf_listener = TransformListener(self._tf_buffer, self)
        if PoseStamped is not None:
            self._object_pose_publisher = self.create_publisher(
                PoseStamped,
                str(self.get_parameter("object_pose_topic").value),
                10,
            )
            self._object_last_seen_publisher = self.create_publisher(
                PoseStamped,
                str(self.get_parameter("object_last_seen_topic").value),
                10,
            )
        self._timer = self.create_timer(1.0 / max(self.precise_rate_hz, 1.0), self._tick)

    @property
    def precise_rate_hz(self) -> float:
        return float(self.get_parameter("precise_rate_hz").value)

    def computation_config(self) -> PrecisePoseComputationConfig:
        """Expose PRECISE geometry settings for tests and later backend hookup."""

        return PrecisePoseComputationConfig(
            output_pose_frame=str(self.get_parameter("output_pose_frame").value),
            last_seen_frame=str(self.get_parameter("object_last_seen_frame").value),
            cube_edge_length_m=DEFAULT_CONTRACTS.cube_edge_length_m,
            min_depth_m=float(self.get_parameter("depth_min_m").value),
            max_depth_m=float(self.get_parameter("depth_max_m").value),
            min_valid_points=int(self.get_parameter("min_valid_points").value),
            max_depth_deviation_m=float(self.get_parameter("max_depth_deviation_m").value),
            max_axis_aligned_extent_m=float(self.get_parameter("max_axis_aligned_extent_m").value),
            min_in_plane_span_m=float(self.get_parameter("min_in_plane_span_m").value),
            max_in_plane_span_m=float(self.get_parameter("max_in_plane_span_m").value),
            max_face_thickness_m=float(self.get_parameter("max_face_thickness_m").value),
        )

    def ingest_candidate(self, candidate: PreciseRoiCandidate) -> None:
        """Owner-local hook for a future segmentation backend or bag replay."""

        self._latest_candidate = candidate
        self._latest_candidate_stamp_s = float(candidate.stamp_s)

    def ingest_depth_image(self, depth_image, stamp_s: Optional[float] = None) -> None:
        """Owner-local hook for aligned depth input or offline replay."""

        self._latest_depth_image = depth_image
        if stamp_s is not None:
            self._latest_depth_stamp_s = float(stamp_s)

    def ingest_intrinsics(self, intrinsics: CameraIntrinsics, stamp_s: Optional[float] = None) -> None:
        """Owner-local hook for camera intrinsics."""

        self._latest_intrinsics = intrinsics
        if stamp_s is not None:
            self._latest_intrinsics_stamp_s = float(stamp_s)

    def runtime_snapshot(self, now_s: float) -> PreciseRuntimeSnapshot:
        """Expose PRECISE runtime readiness for bag/replay tests and diagnostics."""

        return evaluate_precise_runtime_snapshot(
            now_s=now_s,
            candidate_stamp_s=self._latest_candidate_stamp_s,
            depth_stamp_s=self._latest_depth_stamp_s,
            intrinsics_stamp_s=self._latest_intrinsics_stamp_s,
            freshness_timeout_s=float(self.get_parameter("input_freshness_timeout_s").value),
            candidate_topic=str(self.get_parameter("internal_precise_candidate_topic").value),
            depth_topic=str(self.get_parameter("depth_topic").value),
            camera_info_topic=str(self.get_parameter("camera_info_topic").value),
            rgb_topic=str(self.get_parameter("rgb_topic").value),
        )

    def _lookup_rigid_transform(
        self,
        source_frame: str,
        target_frame: str,
        stamp_s: float,
    ) -> Optional[RigidTransform]:
        """Try to resolve a last_seen transform without faking map availability."""

        if source_frame == target_frame:
            return RigidTransform(
                target_frame=target_frame,
                translation_xyz=(0.0, 0.0, 0.0),
                rotation_xyzw=(0.0, 0.0, 0.0, 1.0),
            )
        if self._tf_buffer is None or Duration is None or rclpy is None:
            return None
        try:
            transform = self._tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                rclpy.time.Time(seconds=stamp_s),
                timeout=Duration(seconds=float(self.get_parameter("last_seen_transform_timeout_s").value)),
            )
        except (TransformException, Exception):
            return None
        return RigidTransform(
            target_frame=target_frame,
            translation_xyz=(
                float(transform.transform.translation.x),
                float(transform.transform.translation.y),
                float(transform.transform.translation.z),
            ),
            rotation_xyzw=(
                float(transform.transform.rotation.x),
                float(transform.transform.rotation.y),
                float(transform.transform.rotation.z),
                float(transform.transform.rotation.w),
            ),
        )

    def _tick(self) -> None:
        if not bool(self.get_parameter("enabled").value):
            return

        now_s = 0.0
        if rclpy is not None:
            now_s = self.get_clock().now().nanoseconds / 1_000_000_000.0
        snapshot = self.runtime_snapshot(now_s=now_s)
        if (
            not snapshot.can_estimate_pose
            or self._latest_candidate is None
            or self._latest_depth_image is None
            or self._latest_intrinsics is None
        ):
            self.get_logger().debug("PRECISE pose waiting for candidate, depth image, and intrinsics.")
            return
        if self._object_pose_publisher is None or self._object_last_seen_publisher is None:
            self.get_logger().warn("geometry_msgs/PoseStamped not available; skipping precise public publish.")
            return
        estimate = estimate_precise_pose_from_candidate(
            self._latest_candidate,
            depth_image=self._latest_depth_image,
            intrinsics=self._latest_intrinsics,
            config=self.computation_config(),
        )
        decision = decide_precise_publication(
            estimate,
            last_seen_frame=str(self.get_parameter("object_last_seen_frame").value),
        )
        if not decision.publish_pose:
            self.get_logger().warn(
                "PRECISE pose skipped publish because geometry was implausible or frame handoff was unsafe."
            )
            return

        public_candidate = build_internal_precise_pose_candidate(
            estimate,
            stamp_s=self._latest_candidate.stamp_s,
        )
        self._object_pose_publisher.publish(build_object_pose_msg(public_candidate))
        last_seen_candidate = resolve_last_seen_candidate(
            public_candidate,
            last_seen_frame=str(self.get_parameter("object_last_seen_frame").value),
            transform_provider=self._lookup_rigid_transform,
        )
        if last_seen_candidate is not None:
            self._object_last_seen_publisher.publish(build_object_last_seen_msg(last_seen_candidate))
        else:
            self.get_logger().debug(
                "PRECISE last_seen not updated because no trustworthy map-frame pose is available yet."
            )


def main(args: Optional[Sequence[str]] = None) -> int:
    """Run the ROS node when rclpy is available."""

    if rclpy is None:
        raise RuntimeError("rclpy is required to run object_pose_precise_node")
    rclpy.init(args=args)
    node = ObjectPosePreciseNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0
