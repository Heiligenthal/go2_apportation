from src.go2_object_tracking.go2_object_tracking.contracts import (
    TRACKING_STATE_LOST,
    TRACKING_STATE_OCCLUDED,
    TRACKING_STATE_VISIBLE,
)
from src.go2_object_tracking.go2_object_tracking.msg_adapters import InternalTrackingMeasurement
from src.go2_object_tracking.go2_object_tracking.object_tracker_node import (
    GeometricTargetHints,
    TrackingDecisionFlags,
    TrackerRuntimeState,
    advance_tracker_runtime,
)
from src.go2_object_tracking.go2_object_tracking.map_filter import new_map_tracking_state
from src.go2_object_tracking.go2_object_tracking.throw_logic import ThrowLogicState, ThrowStateMachine


def test_tracker_marks_fresh_fast_measurement_as_visible() -> None:
    previous = TrackerRuntimeState(
        visibility_state=TRACKING_STATE_LOST,
        last_measurement=None,
        last_map_measurement=None,
        map_state=new_map_tracking_state(),
        throw_state=ThrowLogicState(),
        measurement_age_s=float("inf"),
        decision_flags=TrackingDecisionFlags(False, False, True, False, False, False),
        geometric_targets=GeometricTargetHints(None, None, None, False),
    )
    runtime = advance_tracker_runtime(
        previous,
        now_s=10.0,
        incoming_measurement=InternalTrackingMeasurement(
            frame_id="odom",
            center_xyz=(0.1, 0.2, 1.5),
            confidence=0.8,
            stamp_s=9.95,
        ),
        incoming_map_measurement=None,
        visible_timeout_s=0.2,
        occlusion_timeout_s=0.6,
        verify_timeout_s=1.5,
        throw_state_machine=ThrowStateMachine(release_speed_threshold_mps=1.0, confirm_measurements=3),
        min_update_confidence=0.39,
        short_occlusion_timeout_s=1.0,
        local_search_probability_threshold=0.05,
        pick_ready_min_probability=0.40,
        pick_ready_max_speed_mps=0.15,
        precise_pose_available=False,
        precise_pose_age_s=None,
        pick_ready_max_precise_age_s=0.5,
        reposition_requested=False,
        robot_map_position_xyz=None,
        safety_distance_min_m=1.5,
        safety_distance_max_m=2.0,
    )

    assert runtime.visibility_state == TRACKING_STATE_VISIBLE
    assert runtime.last_measurement is not None
    assert runtime.measurement_age_s <= 0.2


def test_tracker_marks_stale_measurement_as_occluded_then_lost() -> None:
    previous = TrackerRuntimeState(
        visibility_state=TRACKING_STATE_VISIBLE,
        last_measurement=InternalTrackingMeasurement(
            frame_id="odom",
            center_xyz=(0.1, 0.2, 1.5),
            confidence=0.8,
            stamp_s=9.7,
        ),
        last_map_measurement=None,
        map_state=new_map_tracking_state(),
        throw_state=ThrowLogicState(),
        measurement_age_s=0.3,
        decision_flags=TrackingDecisionFlags(False, False, True, False, False, False),
        geometric_targets=GeometricTargetHints(None, None, None, False),
    )
    occluded = advance_tracker_runtime(
        previous,
        now_s=10.0,
        incoming_measurement=None,
        incoming_map_measurement=None,
        visible_timeout_s=0.2,
        occlusion_timeout_s=0.6,
        verify_timeout_s=1.5,
        throw_state_machine=ThrowStateMachine(release_speed_threshold_mps=1.0, confirm_measurements=3),
        min_update_confidence=0.39,
        short_occlusion_timeout_s=1.0,
        local_search_probability_threshold=0.05,
        pick_ready_min_probability=0.40,
        pick_ready_max_speed_mps=0.15,
        precise_pose_available=False,
        precise_pose_age_s=None,
        pick_ready_max_precise_age_s=0.5,
        reposition_requested=False,
        robot_map_position_xyz=None,
        safety_distance_min_m=1.5,
        safety_distance_max_m=2.0,
    )
    lost = advance_tracker_runtime(
        occluded,
        now_s=11.5,
        incoming_measurement=None,
        incoming_map_measurement=None,
        visible_timeout_s=0.2,
        occlusion_timeout_s=0.6,
        verify_timeout_s=1.5,
        throw_state_machine=ThrowStateMachine(release_speed_threshold_mps=1.0, confirm_measurements=3),
        min_update_confidence=0.39,
        short_occlusion_timeout_s=1.0,
        local_search_probability_threshold=0.05,
        pick_ready_min_probability=0.40,
        pick_ready_max_speed_mps=0.15,
        precise_pose_available=False,
        precise_pose_age_s=None,
        pick_ready_max_precise_age_s=0.5,
        reposition_requested=False,
        robot_map_position_xyz=None,
        safety_distance_min_m=1.5,
        safety_distance_max_m=2.0,
    )

    assert occluded.visibility_state == TRACKING_STATE_OCCLUDED
    assert lost.visibility_state == TRACKING_STATE_LOST
