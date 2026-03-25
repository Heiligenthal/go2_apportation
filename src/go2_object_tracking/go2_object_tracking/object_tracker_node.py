"""Object tracking with owner-local map filtering and no motion outputs."""

from dataclasses import dataclass
from math import sqrt
from typing import Optional, Sequence, Tuple

try:
    from go2_cube_perception.msg_adapters import InternalMapFastMeasurement
except ImportError:  # pragma: no cover - local pytest path fallback.
    from src.go2_cube_perception.go2_cube_perception.msg_adapters import InternalMapFastMeasurement

from .contracts import (
    DEFAULT_CONTRACTS,
    TRACKING_STATE_LOST,
    TRACKING_STATE_OCCLUDED,
    TRACKING_STATE_REACQUIRE,
    TRACKING_STATE_VISIBLE,
)
from .filter_ballistic import BallisticFilterState, predict_ballistic
from .filter_cv import CvFilterState, predict_cv
from .map_filter import (
    MapTrackingMeasurement,
    MapTrackingState,
    advance_map_filter,
    new_map_tracking_state,
)
from .msg_adapters import (
    InternalPredictionCandidate,
    InternalTrackingMeasurement,
    accept_public_detection_input,
    build_intercept_goal_msg,
    build_object_state_msg,
    build_predicted_region_msg,
    build_throw_status_msg,
)
from .prediction import compute_prediction_gate
from .throw_logic import ThrowLogicState, ThrowStateMachine

try:
    import rclpy
    from rclpy.node import Node
    from go2_apportation_msgs.msg import (
        Detection3DArray,
        InterceptGoal,
        ObjectState,
        PredictedRegion,
        ThrowStatus,
    )
except ImportError:  # pragma: no cover
    rclpy = None
    Node = object  # type: ignore[assignment]
    Detection3DArray = None  # type: ignore[assignment]
    InterceptGoal = None  # type: ignore[assignment]
    ObjectState = None  # type: ignore[assignment]
    PredictedRegion = None  # type: ignore[assignment]
    ThrowStatus = None  # type: ignore[assignment]


@dataclass(frozen=True)
class TrackingDecisionFlags:
    """Owner-local decision outputs for search/reposition/pick gating."""

    short_occluded: bool
    local_search_needed: bool
    global_search_needed: bool
    reposition_needed: bool
    pick_ready: bool
    pick_abort: bool


@dataclass(frozen=True)
class GeometricTargetHints:
    """Owner-local map-based geometry hints without Nav2 or drive-command semantics."""

    reposition_target_map: Optional[Tuple[float, float, float]]
    intercept_target_map: Optional[Tuple[float, float, float]]
    local_search_anchor_map: Optional[Tuple[float, float, float]]
    standoff_band_satisfied: bool


@dataclass(frozen=True)
class TrackerRuntimeState:
    """Owner-local tracker runtime state."""

    visibility_state: str
    last_measurement: Optional[InternalTrackingMeasurement]
    last_map_measurement: Optional[MapTrackingMeasurement]
    map_state: MapTrackingState
    throw_state: ThrowLogicState
    measurement_age_s: float
    decision_flags: TrackingDecisionFlags
    geometric_targets: GeometricTargetHints


@dataclass(frozen=True)
class TrackerInputSnapshot:
    """Runtime snapshot for FAST input consumption."""

    input_mode: str
    public_input_topic: str
    candidate_input_topic: str
    map_input_topic: str
    measurement_ready: bool
    map_measurement_ready: bool


@dataclass(frozen=True)
class ConservativePredictionOutputs:
    """Conservative public prediction outputs derived from the latest public track."""

    predicted_region: InternalPredictionCandidate
    intercept_goal: InternalPredictionCandidate


def _measurement_age_s(
    measurement: Optional[InternalTrackingMeasurement],
    now_s: float,
) -> Optional[float]:
    if measurement is None:
        return None
    return max(0.0, now_s - float(measurement.stamp_s))


def _clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _speed_norm(velocity_xyz: Tuple[float, float, float]) -> float:
    return sqrt(sum(float(value) * float(value) for value in velocity_xyz))


def update_visibility_state(
    previous_state: str,
    *,
    measurement_age_s: Optional[float],
    visible_timeout_s: float,
    occlusion_timeout_s: float,
    verify_timeout_s: float,
) -> str:
    """Map measurements and timeouts to visible/occluded/reacquire/lost."""

    if measurement_age_s is not None and measurement_age_s <= visible_timeout_s:
        return TRACKING_STATE_VISIBLE
    if measurement_age_s is None:
        return TRACKING_STATE_LOST
    if measurement_age_s <= occlusion_timeout_s:
        return TRACKING_STATE_OCCLUDED if previous_state == TRACKING_STATE_VISIBLE else TRACKING_STATE_REACQUIRE
    if measurement_age_s <= verify_timeout_s:
        return TRACKING_STATE_REACQUIRE
    return TRACKING_STATE_LOST


def measurement_from_detection_array(message) -> Optional[InternalTrackingMeasurement]:
    """Extract the strongest available center measurement from Detection3DArray."""

    accept_public_detection_input(message)
    if not message.detections:
        return None
    detection = max(message.detections, key=lambda item: float(item.confidence))
    stamp = 0.0
    if hasattr(message.header, "stamp"):
        stamp = float(message.header.stamp.sec) + (float(message.header.stamp.nanosec) / 1_000_000_000.0)
    return InternalTrackingMeasurement(
        frame_id=message.header.frame_id or DEFAULT_CONTRACTS.state_frame,
        center_xyz=(
            float(detection.pose.pose.position.x),
            float(detection.pose.pose.position.y),
            float(detection.pose.pose.position.z),
        ),
        confidence=float(detection.confidence),
        stamp_s=stamp,
    )


def map_measurement_from_internal(
    measurement: InternalMapFastMeasurement,
) -> MapTrackingMeasurement:
    """Convert cube-perception map measurement into tracking-local form."""

    return MapTrackingMeasurement(
        frame_id=measurement.frame_id,
        position_xyz=measurement.position_map_xyz,
        confidence=float(measurement.measurement_confidence),
        stamp_s=float(measurement.stamp_s),
        source_frame=measurement.source_frame,
        bbox_center_norm_xy=measurement.bbox_center_norm_xy,
        centered=bool(measurement.centered),
    )


def evaluate_tracker_input_snapshot(
    *,
    input_mode: str,
    public_input_topic: str,
    candidate_input_topic: str,
    map_input_topic: str,
    last_measurement: Optional[InternalTrackingMeasurement],
    last_map_measurement: Optional[MapTrackingMeasurement],
    now_s: float,
    visible_timeout_s: float,
) -> TrackerInputSnapshot:
    """Summarize whether the tracker still has fresh public/map input."""

    measurement_ready = False
    if last_measurement is not None:
        measurement_ready = max(0.0, now_s - float(last_measurement.stamp_s)) <= visible_timeout_s
    map_measurement_ready = False
    if last_map_measurement is not None:
        map_measurement_ready = max(0.0, now_s - float(last_map_measurement.stamp_s)) <= visible_timeout_s
    return TrackerInputSnapshot(
        input_mode=input_mode,
        public_input_topic=public_input_topic,
        candidate_input_topic=candidate_input_topic,
        map_input_topic=map_input_topic,
        measurement_ready=measurement_ready,
        map_measurement_ready=map_measurement_ready,
    )


def build_conservative_prediction_outputs(
    measurement: InternalTrackingMeasurement,
    *,
    measurement_age_s: float,
    verify_timeout_s: float,
    state_frame: str,
    predicted_region_size_xyz: Tuple[float, float, float],
    predicted_region_confidence_scale: float,
    predicted_region_valid_for_s: float,
    intercept_goal_approach_radius_m: float,
    intercept_goal_tolerance_m: float,
    intercept_goal_valid_for_s: float,
) -> ConservativePredictionOutputs:
    """Build conservative public prediction/intercept outputs from the latest public track."""

    if verify_timeout_s <= 0.0:
        age_factor = 0.0
    else:
        age_factor = max(0.0, 1.0 - (max(0.0, measurement_age_s) / float(verify_timeout_s)))
    confidence = _clamp_confidence(
        float(measurement.confidence) * float(predicted_region_confidence_scale) * age_factor
    )
    frame_id = measurement.frame_id or state_frame
    predicted_region = InternalPredictionCandidate(
        frame_id=frame_id,
        center_xyz=measurement.center_xyz,
        confidence=confidence,
        stamp_s=measurement.stamp_s,
        valid_for_s=predicted_region_valid_for_s,
        size_xyz=predicted_region_size_xyz,
        approach_radius_m=intercept_goal_approach_radius_m,
        goal_tolerance_m=intercept_goal_tolerance_m,
        is_dynamic_estimate=True,
    )
    intercept_goal = InternalPredictionCandidate(
        frame_id=frame_id,
        center_xyz=measurement.center_xyz,
        confidence=confidence,
        stamp_s=measurement.stamp_s,
        valid_for_s=intercept_goal_valid_for_s,
        size_xyz=predicted_region_size_xyz,
        approach_radius_m=intercept_goal_approach_radius_m,
        goal_tolerance_m=intercept_goal_tolerance_m,
        is_dynamic_estimate=True,
    )
    return ConservativePredictionOutputs(predicted_region=predicted_region, intercept_goal=intercept_goal)


def build_tracking_decision_flags(
    *,
    visibility_state: str,
    measurement_age_s: float,
    map_state: MapTrackingState,
    short_occlusion_timeout_s: float,
    local_search_probability_threshold: float,
    pick_ready_min_probability: float,
    pick_ready_max_speed_mps: float,
    precise_pose_available: bool,
    precise_pose_age_s: Optional[float],
    pick_ready_max_precise_age_s: float,
    reposition_requested: bool,
) -> TrackingDecisionFlags:
    """Build owner-local flags for search, pick, and reposition decisions."""

    short_occluded = (
        map_state.ever_had_fix
        and visibility_state != TRACKING_STATE_VISIBLE
        and measurement_age_s < float(short_occlusion_timeout_s)
    )
    local_search_needed = (
        visibility_state != TRACKING_STATE_VISIBLE
        and map_state.ever_had_fix
        and float(map_state.probability) > float(local_search_probability_threshold)
    )
    global_search_needed = not map_state.ever_had_fix
    speed_mps = _speed_norm(map_state.velocity_xyz)
    precise_age_ok = precise_pose_age_s is not None and precise_pose_age_s <= float(pick_ready_max_precise_age_s)
    pick_ready = bool(
        precise_pose_available
        and precise_age_ok
        and float(map_state.probability) >= float(pick_ready_min_probability)
        and speed_mps <= float(pick_ready_max_speed_mps)
        and visibility_state == TRACKING_STATE_VISIBLE
    )
    pick_abort = bool((not precise_pose_available and map_state.ever_had_fix) or float(map_state.probability) < float(local_search_probability_threshold))
    return TrackingDecisionFlags(
        short_occluded=short_occluded,
        local_search_needed=local_search_needed,
        global_search_needed=global_search_needed,
        reposition_needed=bool(reposition_requested),
        pick_ready=pick_ready,
        pick_abort=pick_abort,
    )


def build_geometric_target_hints(
    *,
    map_state: MapTrackingState,
    robot_map_position_xyz: Optional[Tuple[float, float, float]],
    safety_distance_min_m: float,
    safety_distance_max_m: float,
) -> GeometricTargetHints:
    """Build owner-local map-based reposition/intercept/local-search hints."""

    if not map_state.ever_had_fix:
        return GeometricTargetHints(
            reposition_target_map=None,
            intercept_target_map=None,
            local_search_anchor_map=None,
            standoff_band_satisfied=False,
        )
    intercept_target = tuple(float(value) for value in map_state.position_xyz)
    local_search_anchor = intercept_target
    reposition_target = None
    standoff_band_satisfied = False
    if robot_map_position_xyz is not None:
        dx = float(map_state.position_xyz[0]) - float(robot_map_position_xyz[0])
        dy = float(map_state.position_xyz[1]) - float(robot_map_position_xyz[1])
        dz = float(map_state.position_xyz[2]) - float(robot_map_position_xyz[2])
        distance = sqrt(dx * dx + dy * dy + dz * dz)
        standoff_band_satisfied = float(safety_distance_min_m) <= distance <= float(safety_distance_max_m)
        if distance > 1e-6:
            desired_distance = min(max(distance, float(safety_distance_min_m)), float(safety_distance_max_m))
            scale = max(0.0, (distance - desired_distance) / distance)
            reposition_target = (
                float(robot_map_position_xyz[0]) + dx * scale,
                float(robot_map_position_xyz[1]) + dy * scale,
                float(robot_map_position_xyz[2]) + dz * scale,
            )
    return GeometricTargetHints(
        reposition_target_map=reposition_target,
        intercept_target_map=intercept_target,
        local_search_anchor_map=local_search_anchor,
        standoff_band_satisfied=standoff_band_satisfied,
    )


def advance_tracker_runtime(
    previous_state: TrackerRuntimeState,
    *,
    now_s: float,
    incoming_measurement: Optional[InternalTrackingMeasurement],
    incoming_map_measurement: Optional[MapTrackingMeasurement],
    visible_timeout_s: float,
    occlusion_timeout_s: float,
    verify_timeout_s: float,
    throw_state_machine: ThrowStateMachine,
    min_update_confidence: float,
    short_occlusion_timeout_s: float,
    local_search_probability_threshold: float,
    pick_ready_min_probability: float,
    pick_ready_max_speed_mps: float,
    precise_pose_available: bool,
    precise_pose_age_s: Optional[float],
    pick_ready_max_precise_age_s: float,
    reposition_requested: bool,
    robot_map_position_xyz: Optional[Tuple[float, float, float]],
    safety_distance_min_m: float,
    safety_distance_max_m: float,
) -> TrackerRuntimeState:
    """Advance the tracker with public input plus owner-local map filtering."""

    measurement = incoming_measurement or previous_state.last_measurement
    normalized_map_measurement = incoming_map_measurement
    if normalized_map_measurement is not None and not isinstance(normalized_map_measurement, MapTrackingMeasurement):
        normalized_map_measurement = map_measurement_from_internal(normalized_map_measurement)
    measurement_age = _measurement_age_s(measurement, now_s)
    visibility_state = update_visibility_state(
        previous_state.visibility_state,
        measurement_age_s=measurement_age,
        visible_timeout_s=visible_timeout_s,
        occlusion_timeout_s=occlusion_timeout_s,
        verify_timeout_s=verify_timeout_s,
    )
    map_state = advance_map_filter(
        previous_state.map_state,
        now_s=now_s,
        measurement=normalized_map_measurement,
        min_update_confidence=min_update_confidence,
    )
    throw_state = throw_state_machine.step(
        previous_state.throw_state,
        object_visible=visibility_state in (TRACKING_STATE_VISIBLE, TRACKING_STATE_OCCLUDED),
        speed_mps=_speed_norm(map_state.velocity_xyz),
    )
    decision_flags = build_tracking_decision_flags(
        visibility_state=visibility_state,
        measurement_age_s=measurement_age if measurement_age is not None else float("inf"),
        map_state=map_state,
        short_occlusion_timeout_s=short_occlusion_timeout_s,
        local_search_probability_threshold=local_search_probability_threshold,
        pick_ready_min_probability=pick_ready_min_probability,
        pick_ready_max_speed_mps=pick_ready_max_speed_mps,
        precise_pose_available=precise_pose_available,
        precise_pose_age_s=precise_pose_age_s,
        pick_ready_max_precise_age_s=pick_ready_max_precise_age_s,
        reposition_requested=reposition_requested,
    )
    geometric_targets = build_geometric_target_hints(
        map_state=map_state,
        robot_map_position_xyz=robot_map_position_xyz,
        safety_distance_min_m=safety_distance_min_m,
        safety_distance_max_m=safety_distance_max_m,
    )
    return TrackerRuntimeState(
        visibility_state=visibility_state,
        last_measurement=measurement,
        last_map_measurement=normalized_map_measurement or previous_state.last_map_measurement,
        map_state=map_state,
        throw_state=throw_state,
        measurement_age_s=measurement_age if measurement_age is not None else float("inf"),
        decision_flags=decision_flags,
        geometric_targets=geometric_targets,
    )


class ObjectTrackerNode(Node):
    """Tracking node with owner-local map filter and no movement ownership."""

    def __init__(self) -> None:
        super().__init__("object_tracker_node")
        self.declare_parameter("enabled", False)
        self.declare_parameter("tracker_rate_hz", DEFAULT_CONTRACTS.tracker_rate_hz)
        self.declare_parameter("state_frame", DEFAULT_CONTRACTS.state_frame)
        self.declare_parameter("internal_tracking_frame", DEFAULT_CONTRACTS.internal_tracking_frame)
        self.declare_parameter("best_detection_confidence_threshold", DEFAULT_CONTRACTS.best_detection_confidence_threshold)
        self.declare_parameter("visible_timeout_s", DEFAULT_CONTRACTS.visible_timeout_s)
        self.declare_parameter("occlusion_timeout_s", DEFAULT_CONTRACTS.occlusion_timeout_s)
        self.declare_parameter("verify_timeout_s", DEFAULT_CONTRACTS.verify_timeout_s)
        self.declare_parameter("short_occlusion_timeout_s", DEFAULT_CONTRACTS.short_occlusion_timeout_s)
        self.declare_parameter(
            "local_search_probability_threshold",
            DEFAULT_CONTRACTS.local_search_probability_threshold,
        )
        self.declare_parameter("pick_ready_min_probability", DEFAULT_CONTRACTS.pick_ready_min_probability)
        self.declare_parameter("pick_ready_max_speed_mps", DEFAULT_CONTRACTS.pick_ready_max_speed_mps)
        self.declare_parameter("pick_ready_max_precise_age_s", DEFAULT_CONTRACTS.pick_ready_max_precise_age_s)
        self.declare_parameter("safety_distance_min_m", DEFAULT_CONTRACTS.safety_distance_min_m)
        self.declare_parameter("safety_distance_max_m", DEFAULT_CONTRACTS.safety_distance_max_m)
        self.declare_parameter("release_speed_threshold_mps", DEFAULT_CONTRACTS.release_speed_threshold_mps)
        self.declare_parameter("release_confirm_measurements", DEFAULT_CONTRACTS.release_confirm_measurements)
        self.declare_parameter("gravity_mps2", DEFAULT_CONTRACTS.gravity_mps2)
        self.declare_parameter("use_ballistic_mode", False)
        self.declare_parameter("input_mode", "public_detection3d_array")
        self.declare_parameter("input_topic", DEFAULT_CONTRACTS.fast_input_topic)
        self.declare_parameter("input_topic_candidate", DEFAULT_CONTRACTS.internal_candidate_input_topic)
        self.declare_parameter("input_topic_map_candidate", DEFAULT_CONTRACTS.internal_map_measurement_topic)
        self.declare_parameter("publish_object_state", True)
        self.declare_parameter("publish_throw_status", True)
        self.declare_parameter("publish_predicted_region", True)
        self.declare_parameter("publish_intercept_goal", True)
        self.declare_parameter("object_state_topic", DEFAULT_CONTRACTS.object_state_topic)
        self.declare_parameter("throw_status_topic", DEFAULT_CONTRACTS.throw_status_topic)
        self.declare_parameter("predicted_region_topic", DEFAULT_CONTRACTS.predicted_region_topic)
        self.declare_parameter("intercept_goal_topic", DEFAULT_CONTRACTS.intercept_goal_topic)
        self.declare_parameter("predicted_region_size_x_m", 0.30)
        self.declare_parameter("predicted_region_size_y_m", 0.30)
        self.declare_parameter("predicted_region_size_z_m", 0.20)
        self.declare_parameter("predicted_region_confidence_scale", 0.5)
        self.declare_parameter("predicted_region_valid_for_s", 0.5)
        self.declare_parameter("intercept_goal_approach_radius_m", 0.35)
        self.declare_parameter("intercept_goal_tolerance_m", 0.15)
        self.declare_parameter("intercept_goal_valid_for_s", 0.5)
        self._throw_state_machine = ThrowStateMachine(
            release_speed_threshold_mps=float(self.get_parameter("release_speed_threshold_mps").value),
            confirm_measurements=int(self.get_parameter("release_confirm_measurements").value),
        )
        self._runtime_state = TrackerRuntimeState(
            visibility_state=TRACKING_STATE_LOST,
            last_measurement=None,
            last_map_measurement=None,
            map_state=new_map_tracking_state(frame_id=str(self.get_parameter("internal_tracking_frame").value)),
            throw_state=ThrowLogicState(),
            measurement_age_s=float("inf"),
            decision_flags=TrackingDecisionFlags(False, False, True, False, False, False),
            geometric_targets=GeometricTargetHints(None, None, None, False),
        )
        self._pending_measurement: Optional[InternalTrackingMeasurement] = None
        self._pending_map_measurement: Optional[MapTrackingMeasurement] = None
        self._latest_robot_map_position_xyz: Optional[Tuple[float, float, float]] = None
        self._reposition_requested = False
        self._precise_pose_available = False
        self._precise_pose_stamp_s: Optional[float] = None
        self._fast_input_subscription = None
        self._object_state_publisher = None
        self._throw_status_publisher = None
        self._predicted_region_publisher = None
        self._intercept_goal_publisher = None
        if Detection3DArray is not None:
            self._fast_input_subscription = self.create_subscription(
                Detection3DArray,
                str(self.get_parameter("input_topic").value),
                self._on_public_fast_input,
                10,
            )
        if ObjectState is not None:
            self._object_state_publisher = self.create_publisher(
                ObjectState,
                str(self.get_parameter("object_state_topic").value),
                10,
            )
        if ThrowStatus is not None:
            self._throw_status_publisher = self.create_publisher(
                ThrowStatus,
                str(self.get_parameter("throw_status_topic").value),
                10,
            )
        if PredictedRegion is not None:
            self._predicted_region_publisher = self.create_publisher(
                PredictedRegion,
                str(self.get_parameter("predicted_region_topic").value),
                10,
            )
        if InterceptGoal is not None:
            self._intercept_goal_publisher = self.create_publisher(
                InterceptGoal,
                str(self.get_parameter("intercept_goal_topic").value),
                10,
            )
        self._timer = self.create_timer(1.0 / max(self.tracker_rate_hz, 1.0), self._tick)

    @property
    def tracker_rate_hz(self) -> float:
        return float(self.get_parameter("tracker_rate_hz").value)

    def ingest_map_measurement(self, measurement: InternalMapFastMeasurement) -> None:
        """Accept owner-local map measurement from the FAST stage."""

        self._pending_map_measurement = map_measurement_from_internal(measurement)

    def ingest_robot_map_position(self, position_xyz: Tuple[float, float, float]) -> None:
        """Accept owner-local robot map position for standoff geometry only."""

        self._latest_robot_map_position_xyz = tuple(float(value) for value in position_xyz)

    def ingest_observe_feedback(self, *, reposition_needed: bool) -> None:
        """Accept owner-local camera centering feedback without creating new public topics."""

        self._reposition_requested = bool(reposition_needed)

    def ingest_precise_pose_validity(self, *, is_valid: bool, stamp_s: Optional[float] = None) -> None:
        """Accept owner-local PRECISE validity for pick-ready/pick-abort gating."""

        self._precise_pose_available = bool(is_valid)
        if stamp_s is not None:
            self._precise_pose_stamp_s = float(stamp_s)

    def _on_public_fast_input(self, message) -> None:
        measurement = measurement_from_detection_array(message)
        if measurement is not None:
            self._pending_measurement = measurement

    def input_snapshot(self, now_s: float) -> TrackerInputSnapshot:
        """Expose tracking input readiness for bag/replay diagnostics."""

        return evaluate_tracker_input_snapshot(
            input_mode=str(self.get_parameter("input_mode").value),
            public_input_topic=str(self.get_parameter("input_topic").value),
            candidate_input_topic=str(self.get_parameter("input_topic_candidate").value),
            map_input_topic=str(self.get_parameter("input_topic_map_candidate").value),
            last_measurement=self._pending_measurement or self._runtime_state.last_measurement,
            last_map_measurement=self._pending_map_measurement or self._runtime_state.last_map_measurement,
            now_s=now_s,
            visible_timeout_s=float(self.get_parameter("visible_timeout_s").value),
        )

    def current_map_state(self) -> MapTrackingState:
        """Expose owner-local map filter state for tests and diagnostics."""

        return self._runtime_state.map_state

    def current_decision_flags(self) -> TrackingDecisionFlags:
        """Expose owner-local decision flags for tests and diagnostics."""

        return self._runtime_state.decision_flags

    def current_geometric_targets(self) -> GeometricTargetHints:
        """Expose owner-local geometric target hints for tests and diagnostics."""

        return self._runtime_state.geometric_targets

    def _tick(self) -> None:
        if not bool(self.get_parameter("enabled").value):
            return

        now = self.get_clock().now().nanoseconds / 1_000_000_000.0
        precise_age_s = None
        if self._precise_pose_stamp_s is not None:
            precise_age_s = max(0.0, now - float(self._precise_pose_stamp_s))
        self._runtime_state = advance_tracker_runtime(
            self._runtime_state,
            now_s=now,
            incoming_measurement=self._pending_measurement,
            incoming_map_measurement=self._pending_map_measurement,
            visible_timeout_s=float(self.get_parameter("visible_timeout_s").value),
            occlusion_timeout_s=float(self.get_parameter("occlusion_timeout_s").value),
            verify_timeout_s=float(self.get_parameter("verify_timeout_s").value),
            throw_state_machine=self._throw_state_machine,
            min_update_confidence=float(self.get_parameter("best_detection_confidence_threshold").value),
            short_occlusion_timeout_s=float(self.get_parameter("short_occlusion_timeout_s").value),
            local_search_probability_threshold=float(
                self.get_parameter("local_search_probability_threshold").value
            ),
            pick_ready_min_probability=float(self.get_parameter("pick_ready_min_probability").value),
            pick_ready_max_speed_mps=float(self.get_parameter("pick_ready_max_speed_mps").value),
            precise_pose_available=self._precise_pose_available,
            precise_pose_age_s=precise_age_s,
            pick_ready_max_precise_age_s=float(self.get_parameter("pick_ready_max_precise_age_s").value),
            reposition_requested=self._reposition_requested,
            robot_map_position_xyz=self._latest_robot_map_position_xyz,
            safety_distance_min_m=float(self.get_parameter("safety_distance_min_m").value),
            safety_distance_max_m=float(self.get_parameter("safety_distance_max_m").value),
        )
        if (
            bool(self.get_parameter("publish_object_state").value)
            and self._runtime_state.last_measurement is not None
            and self._object_state_publisher is not None
        ):
            self._object_state_publisher.publish(build_object_state_msg(self._runtime_state.last_measurement))
        if bool(self.get_parameter("publish_throw_status").value) and self._throw_status_publisher is not None:
            stamp_s = (
                self._runtime_state.last_measurement.stamp_s
                if self._runtime_state.last_measurement is not None
                else now
            )
            self._throw_status_publisher.publish(
                build_throw_status_msg(
                    self._runtime_state.throw_state.status,
                    frame_id=str(self.get_parameter("state_frame").value),
                    stamp_s=stamp_s,
                )
            )
        if self._runtime_state.last_measurement is not None:
            public_outputs = build_conservative_prediction_outputs(
                self._runtime_state.last_measurement,
                measurement_age_s=self._runtime_state.measurement_age_s,
                verify_timeout_s=float(self.get_parameter("verify_timeout_s").value),
                state_frame=str(self.get_parameter("state_frame").value),
                predicted_region_size_xyz=(
                    float(self.get_parameter("predicted_region_size_x_m").value),
                    float(self.get_parameter("predicted_region_size_y_m").value),
                    float(self.get_parameter("predicted_region_size_z_m").value),
                ),
                predicted_region_confidence_scale=float(
                    self.get_parameter("predicted_region_confidence_scale").value
                ),
                predicted_region_valid_for_s=float(self.get_parameter("predicted_region_valid_for_s").value),
                intercept_goal_approach_radius_m=float(
                    self.get_parameter("intercept_goal_approach_radius_m").value
                ),
                intercept_goal_tolerance_m=float(self.get_parameter("intercept_goal_tolerance_m").value),
                intercept_goal_valid_for_s=float(self.get_parameter("intercept_goal_valid_for_s").value),
            )
            if bool(self.get_parameter("publish_predicted_region").value) and self._predicted_region_publisher is not None:
                self._predicted_region_publisher.publish(build_predicted_region_msg(public_outputs.predicted_region))
            if bool(self.get_parameter("publish_intercept_goal").value) and self._intercept_goal_publisher is not None:
                self._intercept_goal_publisher.publish(build_intercept_goal_msg(public_outputs.intercept_goal))
        self._pending_measurement = None
        self._pending_map_measurement = None
        self._reposition_requested = False
        compute_prediction_gate(
            speed_mps=_speed_norm(self._runtime_state.map_state.velocity_xyz),
            occlusion_s=max(0.0, self._runtime_state.measurement_age_s),
            max_radius_m=1.0,
        )
        predict_cv(
            CvFilterState(self._runtime_state.map_state.position_xyz, self._runtime_state.map_state.velocity_xyz, 0.0),
            0.0,
        )
        predict_ballistic(
            BallisticFilterState(
                self._runtime_state.map_state.position_xyz,
                self._runtime_state.map_state.velocity_xyz,
                0.0,
            ),
            0.0,
            gravity_mps2=float(self.get_parameter("gravity_mps2").value),
        )


def main(args: Optional[Sequence[str]] = None) -> int:
    """Run the ROS node when rclpy is available."""

    if rclpy is None:
        raise RuntimeError("rclpy is required to run object_tracker_node")
    rclpy.init(args=args)
    node = ObjectTrackerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0
