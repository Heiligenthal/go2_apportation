from src.go2_object_tracking.go2_object_tracking.map_filter import new_map_tracking_state
from src.go2_object_tracking.go2_object_tracking.object_tracker_node import (
    build_geometric_target_hints,
    build_tracking_decision_flags,
)


def test_tracking_decision_flags_distinguish_local_and_global_search() -> None:
    never_seen = new_map_tracking_state()
    global_flags = build_tracking_decision_flags(
        visibility_state="lost",
        measurement_age_s=2.0,
        map_state=never_seen,
        short_occlusion_timeout_s=1.0,
        local_search_probability_threshold=0.05,
        pick_ready_min_probability=0.40,
        pick_ready_max_speed_mps=0.15,
        precise_pose_available=False,
        precise_pose_age_s=None,
        pick_ready_max_precise_age_s=0.5,
        reposition_requested=False,
    )

    seen = new_map_tracking_state()
    seen = seen.__class__(
        frame_id="map",
        position_xyz=(2.0, 0.0, 0.0),
        velocity_xyz=(0.0, 0.0, 0.0),
        acceleration_xyz=(0.0, 0.0, 0.0),
        probability=0.3,
        stamp_s=1.0,
        covariance_diag=(0.1, 0.1, 0.1),
        source_frame="camera_link",
        bbox_center_norm_xy=(0.2, 0.0),
        centered=False,
        ever_had_fix=True,
        axis_states=seen.axis_states,
    )
    local_flags = build_tracking_decision_flags(
        visibility_state="occluded",
        measurement_age_s=0.5,
        map_state=seen,
        short_occlusion_timeout_s=1.0,
        local_search_probability_threshold=0.05,
        pick_ready_min_probability=0.40,
        pick_ready_max_speed_mps=0.15,
        precise_pose_available=False,
        precise_pose_age_s=None,
        pick_ready_max_precise_age_s=0.5,
        reposition_requested=True,
    )

    assert global_flags.global_search_needed is True
    assert local_flags.local_search_needed is True
    assert local_flags.short_occluded is True
    assert local_flags.reposition_needed is True


def test_geometric_target_hints_respect_safety_band() -> None:
    state = new_map_tracking_state()
    state = state.__class__(
        frame_id="map",
        position_xyz=(3.0, 0.0, 0.0),
        velocity_xyz=(0.0, 0.0, 0.0),
        acceleration_xyz=(0.0, 0.0, 0.0),
        probability=0.7,
        stamp_s=1.0,
        covariance_diag=(0.1, 0.1, 0.1),
        source_frame="camera_link",
        bbox_center_norm_xy=(0.0, 0.0),
        centered=True,
        ever_had_fix=True,
        axis_states=state.axis_states,
    )
    hints = build_geometric_target_hints(
        map_state=state,
        robot_map_position_xyz=(0.0, 0.0, 0.0),
        safety_distance_min_m=1.5,
        safety_distance_max_m=2.0,
    )

    assert hints.intercept_target_map == (3.0, 0.0, 0.0)
    assert hints.local_search_anchor_map == (3.0, 0.0, 0.0)
    assert hints.reposition_target_map is not None
    assert hints.standoff_band_satisfied is False
