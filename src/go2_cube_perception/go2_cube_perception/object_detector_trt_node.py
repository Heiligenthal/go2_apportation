"""TensorRT detector skeleton for cube FAST perception."""

from dataclasses import dataclass
from typing import Optional, Protocol, Sequence, Tuple

from .backend_types import BackendKind
from .contracts import DEFAULT_CONTRACTS
from . import topics
from .depth_roi import BoundingBox2D
from .msg_adapters import build_object_visible_msg
from .look_control import (
    LOOK_MODE_INTERCEPT_FAST,
    LOOK_MODE_OBSERVE_FAST,
    LookControllerConfig,
    LookControllerState,
    compute_normalized_bbox_error,
    is_centered,
    step_look_controller,
)

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Vector3
    from std_msgs.msg import Bool, Float32
except ImportError:  # pragma: no cover - enables pure-python unit tests.
    rclpy = None
    Node = object  # type: ignore[assignment]
    Vector3 = None  # type: ignore[assignment]
    Bool = None  # type: ignore[assignment]
    Float32 = None  # type: ignore[assignment]


@dataclass(frozen=True)
class DetectorStatus:
    """Small status snapshot for tests and diagnostics."""

    enabled: bool
    backend_kind: str
    gpu_required: bool
    model_configured: bool
    ready_outputs: Tuple[str, ...]


@dataclass(frozen=True)
class DetectorRuntimeSnapshot:
    """Bag-/runtime-friendly detector input snapshot."""

    rgb_topic: str
    camera_info_topic: str
    internal_candidate_topic: str
    object_visible_topic: str
    rgb_ready: bool
    camera_info_ready: bool
    candidate_ready: bool
    can_publish_visible: bool
    look_outputs_enabled: bool


@dataclass(frozen=True)
class Detector2DCandidate:
    """Owner-local detector result that the FAST depth stage can consume."""

    bbox: BoundingBox2D
    confidence: float
    class_id: int = 1
    frame_id: str = ""
    stamp_s: float = 0.0
    source_hint: str = "detector_backend"
    bbox_center_norm_xy: Tuple[float, float] = (0.0, 0.0)
    centered: bool = False
    image_size_wh: Tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class DetectorBackendConfig:
    """Future TensorRT backend scaffold without requiring an engine today."""

    backend_kind: str
    engine_path: str
    model_weights_path: str
    input_width: int
    input_height: int
    confidence_threshold: float
    nms_iou_threshold: float
    max_detections: int


class DetectorBackend(Protocol):
    """Small backend contract for later YOLOv8n TensorRT integration."""

    def infer(self) -> Sequence[Detector2DCandidate]:
        """Return owner-local 2D candidates without choosing a public message."""


def build_backend_config(
    *,
    backend_kind: str,
    engine_path: str,
    model_weights_path: str,
    input_width: int,
    input_height: int,
    confidence_threshold: float,
    nms_iou_threshold: float,
    max_detections: int,
) -> DetectorBackendConfig:
    """Build a validated detector backend scaffold."""

    return DetectorBackendConfig(
        backend_kind=backend_kind,
        engine_path=engine_path,
        model_weights_path=model_weights_path,
        input_width=max(1, int(input_width)),
        input_height=max(1, int(input_height)),
        confidence_threshold=max(0.0, min(1.0, float(confidence_threshold))),
        nms_iou_threshold=max(0.0, min(1.0, float(nms_iou_threshold))),
        max_detections=max(1, int(max_detections)),
    )


def select_best_candidate(
    candidates: Sequence[Detector2DCandidate],
    *,
    confidence_threshold: float,
) -> Optional[Detector2DCandidate]:
    """Pick the strongest valid candidate for the single active cube."""

    accepted = [candidate for candidate in candidates if candidate.confidence >= confidence_threshold]
    if not accepted:
        return None
    return max(accepted, key=lambda candidate: candidate.confidence)


def _is_fresh(stamp_s: Optional[float], now_s: float, freshness_timeout_s: float) -> bool:
    if stamp_s is None:
        return False
    return max(0.0, now_s - float(stamp_s)) <= freshness_timeout_s


def enrich_candidate_geometry(
    candidate: Detector2DCandidate,
    *,
    image_size_wh: Tuple[int, int],
) -> Detector2DCandidate:
    """Attach normalized image-plane geometry for owner-local look logic."""

    ex, ey = compute_normalized_bbox_error(
        bbox_center_uv=(candidate.bbox.center_u, candidate.bbox.center_v),
        image_size_wh=image_size_wh,
    )
    return Detector2DCandidate(
        bbox=candidate.bbox,
        confidence=float(candidate.confidence),
        class_id=int(candidate.class_id),
        frame_id=candidate.frame_id,
        stamp_s=float(candidate.stamp_s),
        source_hint=candidate.source_hint,
        bbox_center_norm_xy=(float(ex), float(ey)),
        centered=is_centered(ex=ex, ey=ey),
        image_size_wh=(max(1, int(image_size_wh[0])), max(1, int(image_size_wh[1]))),
    )


def evaluate_detector_runtime_snapshot(
    *,
    now_s: float,
    candidate: Optional[Detector2DCandidate],
    rgb_stamp_s: Optional[float],
    camera_info_stamp_s: Optional[float],
    freshness_timeout_s: float,
    rgb_required: bool,
    camera_info_required: bool,
    rgb_topic: str,
    camera_info_topic: str,
    internal_candidate_topic: str,
    object_visible_topic: str,
    look_outputs_enabled: bool,
) -> DetectorRuntimeSnapshot:
    """Summarize detector readiness without depending on ROS runtime."""

    rgb_ready = (not rgb_required) or _is_fresh(rgb_stamp_s, now_s, freshness_timeout_s)
    camera_info_ready = (not camera_info_required) or _is_fresh(
        camera_info_stamp_s, now_s, freshness_timeout_s
    )
    candidate_ready = candidate is not None and _is_fresh(
        getattr(candidate, "stamp_s", None),
        now_s,
        freshness_timeout_s,
    )
    return DetectorRuntimeSnapshot(
        rgb_topic=rgb_topic,
        camera_info_topic=camera_info_topic,
        internal_candidate_topic=internal_candidate_topic,
        object_visible_topic=object_visible_topic,
        rgb_ready=rgb_ready,
        camera_info_ready=camera_info_ready,
        candidate_ready=candidate_ready,
        can_publish_visible=rgb_ready and camera_info_ready,
        look_outputs_enabled=bool(look_outputs_enabled),
    )


class ObjectDetectorTrtNode(Node):
    """GPU-first detector skeleton without real inference."""

    def __init__(self) -> None:
        super().__init__("object_detector_trt_node")
        self.declare_parameter("enabled", False)
        self.declare_parameter("backend_kind", DEFAULT_CONTRACTS.default_detector_backend.value)
        self.declare_parameter("gpu_required", DEFAULT_CONTRACTS.gpu_first_required)
        self.declare_parameter("detector_rate_hz", 30.0)
        self.declare_parameter("model_weights_path", "")
        self.declare_parameter("engine_path", "")
        self.declare_parameter("input_width", 640)
        self.declare_parameter("input_height", 640)
        self.declare_parameter("confidence_threshold", DEFAULT_CONTRACTS.best_detection_confidence_threshold)
        self.declare_parameter("nms_iou_threshold", 0.5)
        self.declare_parameter("max_detections", 1)
        self.declare_parameter("rgb_topic", topics.RGB_IMAGE)
        self.declare_parameter("camera_info_topic", topics.CAMERA_INFO)
        self.declare_parameter("input_freshness_timeout_s", 0.5)
        self.declare_parameter("rgb_required", False)
        self.declare_parameter("camera_info_required", False)
        self.declare_parameter("ingest_mode", "owner_local_candidate")
        self.declare_parameter("object_visible_topic", topics.OBJECT_VISIBLE)
        self.declare_parameter("publish_debug_bbox", False)
        self.declare_parameter("internal_bbox_topic", topics.INTERNAL_CUBE_BBOX)
        self.declare_parameter("publish_bridge_look_outputs", False)
        self.declare_parameter("look_control_mode", LOOK_MODE_OBSERVE_FAST)
        self.declare_parameter("look_yaw_topic", topics.LOOK_YAW_DELTA)
        self.declare_parameter("balance_rpy_topic", topics.BALANCE_RPY_CMD)
        self.declare_parameter("look_yaw_kp", 0.8)
        self.declare_parameter("look_pitch_kp", 0.6)
        self.declare_parameter("look_deadband_norm", 0.03)
        self.declare_parameter("look_yaw_rate_limit_rps", 0.8)
        self.declare_parameter("look_pitch_rate_limit_rps", 0.5)
        self.declare_parameter("observe_center_dwell_s", 0.6)
        self.declare_parameter("observe_reposition_no_improvement_s", 0.8)
        self.declare_parameter("observe_improvement_epsilon", 0.02)
        self.declare_parameter("look_center_half_extent_norm", 0.125)
        self._visible_publisher = self.create_publisher(
            Bool,
            str(self.get_parameter("object_visible_topic").value),
            10,
        )
        self._look_yaw_publisher = None
        self._balance_rpy_publisher = None
        if Float32 is not None:
            self._look_yaw_publisher = self.create_publisher(
                Float32,
                str(self.get_parameter("look_yaw_topic").value),
                10,
            )
        if Vector3 is not None:
            self._balance_rpy_publisher = self.create_publisher(
                Vector3,
                str(self.get_parameter("balance_rpy_topic").value),
                10,
            )
        self._latest_candidate: Optional[Detector2DCandidate] = None
        self._latest_rgb_stamp_s: Optional[float] = None
        self._latest_camera_info_stamp_s: Optional[float] = None
        self._look_state = LookControllerState()
        self._timer = self.create_timer(1.0 / max(self.detector_rate_hz, 1.0), self._tick)

    @property
    def detector_rate_hz(self) -> float:
        return float(self.get_parameter("detector_rate_hz").value)

    def status(self) -> DetectorStatus:
        """Expose node status without touching ROS messages."""

        model_weights_path = str(self.get_parameter("model_weights_path").value)
        engine_path = str(self.get_parameter("engine_path").value)
        return DetectorStatus(
            enabled=bool(self.get_parameter("enabled").value),
            backend_kind=str(self.get_parameter("backend_kind").value),
            gpu_required=bool(self.get_parameter("gpu_required").value),
            model_configured=bool(model_weights_path or engine_path),
            ready_outputs=topics.READY_PUBLIC_OUTPUT_TOPICS,
        )

    def backend_config(self) -> DetectorBackendConfig:
        """Expose the backend contract for tests and future engine hookup."""

        return build_backend_config(
            backend_kind=str(self.get_parameter("backend_kind").value),
            engine_path=str(self.get_parameter("engine_path").value),
            model_weights_path=str(self.get_parameter("model_weights_path").value),
            input_width=int(self.get_parameter("input_width").value),
            input_height=int(self.get_parameter("input_height").value),
            confidence_threshold=float(self.get_parameter("confidence_threshold").value),
            nms_iou_threshold=float(self.get_parameter("nms_iou_threshold").value),
            max_detections=int(self.get_parameter("max_detections").value),
        )

    def ingest_mock_candidate(self, candidate: Optional[Detector2DCandidate]) -> None:
        """Owner-local hook for tests and bag-driven dry runs without TensorRT."""

        if candidate is None:
            self._latest_candidate = None
            return
        image_size = candidate.image_size_wh
        if image_size[0] <= 0 or image_size[1] <= 0:
            image_size = (
                int(self.get_parameter("input_width").value),
                int(self.get_parameter("input_height").value),
            )
        self._latest_candidate = enrich_candidate_geometry(candidate, image_size_wh=image_size)

    def ingest_rgb_stamp(self, stamp_s: float) -> None:
        """Owner-local hook for RGB arrival tracking in replay/runtime tests."""

        self._latest_rgb_stamp_s = float(stamp_s)

    def ingest_camera_info_stamp(self, stamp_s: float) -> None:
        """Owner-local hook for CameraInfo arrival tracking in replay/runtime tests."""

        self._latest_camera_info_stamp_s = float(stamp_s)

    def runtime_snapshot(self, now_s: float) -> DetectorRuntimeSnapshot:
        """Expose runtime readiness for bag/replay tests and diagnostics."""

        return evaluate_detector_runtime_snapshot(
            now_s=now_s,
            candidate=self._latest_candidate,
            rgb_stamp_s=self._latest_rgb_stamp_s,
            camera_info_stamp_s=self._latest_camera_info_stamp_s,
            freshness_timeout_s=float(self.get_parameter("input_freshness_timeout_s").value),
            rgb_required=bool(self.get_parameter("rgb_required").value),
            camera_info_required=bool(self.get_parameter("camera_info_required").value),
            rgb_topic=str(self.get_parameter("rgb_topic").value),
            camera_info_topic=str(self.get_parameter("camera_info_topic").value),
            internal_candidate_topic=str(self.get_parameter("internal_bbox_topic").value),
            object_visible_topic=str(self.get_parameter("object_visible_topic").value),
            look_outputs_enabled=bool(self.get_parameter("publish_bridge_look_outputs").value),
        )

    def look_controller_config(self) -> LookControllerConfig:
        """Expose look-control parameters for tests and diagnostics."""

        return LookControllerConfig(
            yaw_kp=float(self.get_parameter("look_yaw_kp").value),
            pitch_kp=float(self.get_parameter("look_pitch_kp").value),
            deadband_norm=float(self.get_parameter("look_deadband_norm").value),
            yaw_rate_limit_rps=float(self.get_parameter("look_yaw_rate_limit_rps").value),
            pitch_rate_limit_rps=float(self.get_parameter("look_pitch_rate_limit_rps").value),
            centered_half_extent_norm=float(self.get_parameter("look_center_half_extent_norm").value),
            centered_dwell_s=float(self.get_parameter("observe_center_dwell_s").value),
            reposition_no_improvement_s=float(
                self.get_parameter("observe_reposition_no_improvement_s").value
            ),
            improvement_epsilon=float(self.get_parameter("observe_improvement_epsilon").value),
        )

    def _tick(self) -> None:
        """Keep the node startable without weights or inference code."""

        if not bool(self.get_parameter("enabled").value):
            return

        backend_kind = str(self.get_parameter("backend_kind").value)
        if backend_kind not in {kind.value for kind in BackendKind}:
            self.get_logger().warn(f"Unknown detector backend '{backend_kind}', staying in stub mode.")
            return

        now_s = 0.0
        if rclpy is not None:
            now_s = self.get_clock().now().nanoseconds / 1_000_000_000.0
        snapshot = self.runtime_snapshot(now_s=now_s)
        if not snapshot.can_publish_visible:
            self.get_logger().debug("Detector runtime waiting for required RGB/camera_info freshness.")
            return

        # TODO: Hook a real TensorRT YOLOv8n backend into DetectorBackend once runtime assets are provided.
        best_candidate = select_best_candidate(
            [candidate for candidate in [self._latest_candidate] if candidate is not None],
            confidence_threshold=self.backend_config().confidence_threshold,
        )
        msg = build_object_visible_msg(best_candidate is not None)
        self._visible_publisher.publish(msg)
        if (
            best_candidate is None
            or not bool(self.get_parameter("publish_bridge_look_outputs").value)
            or self._look_yaw_publisher is None
        ):
            return

        mode = str(self.get_parameter("look_control_mode").value)
        if mode not in {LOOK_MODE_OBSERVE_FAST, LOOK_MODE_INTERCEPT_FAST}:
            mode = LOOK_MODE_OBSERVE_FAST
        self._look_state, look_output = step_look_controller(
            self._look_state,
            now_s=now_s,
            ex=float(best_candidate.bbox_center_norm_xy[0]),
            ey=float(best_candidate.bbox_center_norm_xy[1]),
            mode=mode,
            config=self.look_controller_config(),
        )
        yaw_msg = Float32()
        yaw_msg.data = float(look_output.yaw_delta)
        self._look_yaw_publisher.publish(yaw_msg)
        if mode == LOOK_MODE_OBSERVE_FAST and self._balance_rpy_publisher is not None:
            balance_msg = Vector3()
            balance_msg.x = float(look_output.balance_rpy[0])
            balance_msg.y = float(look_output.balance_rpy[1])
            balance_msg.z = float(look_output.balance_rpy[2])
            self._balance_rpy_publisher.publish(balance_msg)


def main(args: Optional[Sequence[str]] = None) -> int:
    """Run the ROS node when rclpy is available."""

    if rclpy is None:
        raise RuntimeError("rclpy is required to run object_detector_trt_node")
    rclpy.init(args=args)
    node = ObjectDetectorTrtNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0
