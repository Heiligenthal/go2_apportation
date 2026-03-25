"""Thin owner-local convenience contracts for object tracking."""

from dataclasses import dataclass
from typing import Tuple


TRACKING_STATE_VISIBLE = "visible"
TRACKING_STATE_OCCLUDED = "occluded"
TRACKING_STATE_REACQUIRE = "reacquire"
TRACKING_STATE_LOST = "lost"

THROW_STATUS_IDLE = "IDLE"
THROW_STATUS_HELD = "HELD"
THROW_STATUS_RELEASE_SUSPECTED = "RELEASE_SUSPECTED"
THROW_STATUS_THROWN = "THROWN"
THROW_STATUS_LANDED = "LANDED"
THROW_STATUS_LOST = "LOST"


@dataclass(frozen=True)
class TrackingContracts:
    """Document-/freeze-derived owner mirror without introducing new shared truth."""

    state_frame: str = "odom"
    internal_tracking_frame: str = "map"
    tracker_rate_hz: float = 30.0
    best_detection_confidence_threshold: float = 0.39
    visible_timeout_s: float = 0.2
    occlusion_timeout_s: float = 0.6
    verify_timeout_s: float = 1.5
    short_occlusion_timeout_s: float = 1.0
    local_search_probability_threshold: float = 0.05
    pick_ready_min_probability: float = 0.40
    pick_ready_max_speed_mps: float = 0.15
    pick_ready_max_precise_age_s: float = 0.5
    safety_distance_min_m: float = 1.5
    safety_distance_max_m: float = 2.0
    gravity_mps2: float = 9.81
    release_speed_threshold_mps: float = 1.0
    release_confirm_measurements: int = 3
    public_safe_topics: Tuple[str, ...] = (
        "/tracking/object_state",
        "/tracking/throw_status",
        "/tracking/predicted_region",
        "/tracking/intercept_goal",
    )
    fast_input_topic: str = "/tracking/detections3d_fast"
    fast_input_wire_type: str = "go2_apportation_msgs/Detection3DArray"
    object_state_topic: str = "/tracking/object_state"
    object_state_wire_type: str = "go2_apportation_msgs/ObjectState"
    throw_status_topic: str = "/tracking/throw_status"
    throw_status_wire_type: str = "go2_apportation_msgs/ThrowStatus"
    predicted_region_topic: str = "/tracking/predicted_region"
    predicted_region_wire_type: str = "go2_apportation_msgs/PredictedRegion"
    intercept_goal_topic: str = "/tracking/intercept_goal"
    intercept_goal_wire_type: str = "go2_apportation_msgs/InterceptGoal"
    blocked_by_h06_topics: Tuple[str, ...] = ()
    blocked_or_unclear_topics: Tuple[str, ...] = ()
    internal_candidate_input_topic: str = "/tracking/internal/detections3d_fast_candidate"
    internal_map_measurement_topic: str = "/tracking/internal/cube_measurement_map"


DEFAULT_CONTRACTS = TrackingContracts()
