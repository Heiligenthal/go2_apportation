from src.go2_object_tracking.go2_object_tracking.contracts import DEFAULT_CONTRACTS
from src.go2_object_tracking.go2_object_tracking import msg_adapters
from src.go2_object_tracking.go2_object_tracking.msg_adapters import InternalTrackingMeasurement
from src.go2_object_tracking.go2_object_tracking.object_tracker_node import (
    build_conservative_prediction_outputs,
)


def test_conservative_prediction_outputs_stay_odom_led_and_complete() -> None:
    measurement = InternalTrackingMeasurement(
        frame_id="odom",
        center_xyz=(0.7, 0.1, 0.4),
        confidence=0.8,
        stamp_s=9.0,
    )

    outputs = build_conservative_prediction_outputs(
        measurement,
        measurement_age_s=0.25,
        verify_timeout_s=1.5,
        state_frame=DEFAULT_CONTRACTS.state_frame,
        predicted_region_size_xyz=(0.3, 0.3, 0.2),
        predicted_region_confidence_scale=0.5,
        predicted_region_valid_for_s=0.5,
        intercept_goal_approach_radius_m=0.35,
        intercept_goal_tolerance_m=0.15,
        intercept_goal_valid_for_s=0.5,
    )

    assert outputs.predicted_region.frame_id == "odom"
    assert outputs.intercept_goal.frame_id == "odom"
    assert outputs.predicted_region.center_xyz == measurement.center_xyz
    assert outputs.intercept_goal.center_xyz == measurement.center_xyz
    assert outputs.predicted_region.size_xyz == (0.3, 0.3, 0.2)
    assert outputs.intercept_goal.approach_radius_m == 0.35
    assert outputs.intercept_goal.goal_tolerance_m == 0.15
    assert 0.0 <= outputs.predicted_region.confidence <= 1.0
    assert outputs.predicted_region.valid_for_s == 0.5
    assert outputs.intercept_goal.valid_for_s == 0.5


def test_conservative_prediction_confidence_decays_with_measurement_age() -> None:
    measurement = InternalTrackingMeasurement(
        frame_id="odom",
        center_xyz=(0.0, 0.0, 1.0),
        confidence=0.9,
        stamp_s=1.0,
    )

    fresh = build_conservative_prediction_outputs(
        measurement,
        measurement_age_s=0.1,
        verify_timeout_s=1.5,
        state_frame=DEFAULT_CONTRACTS.state_frame,
        predicted_region_size_xyz=(0.3, 0.3, 0.2),
        predicted_region_confidence_scale=0.5,
        predicted_region_valid_for_s=0.5,
        intercept_goal_approach_radius_m=0.35,
        intercept_goal_tolerance_m=0.15,
        intercept_goal_valid_for_s=0.5,
    )
    stale = build_conservative_prediction_outputs(
        measurement,
        measurement_age_s=1.6,
        verify_timeout_s=1.5,
        state_frame=DEFAULT_CONTRACTS.state_frame,
        predicted_region_size_xyz=(0.3, 0.3, 0.2),
        predicted_region_confidence_scale=0.5,
        predicted_region_valid_for_s=0.5,
        intercept_goal_approach_radius_m=0.35,
        intercept_goal_tolerance_m=0.15,
        intercept_goal_valid_for_s=0.5,
    )

    assert fresh.predicted_region.confidence > stale.predicted_region.confidence
    assert stale.predicted_region.confidence == 0.0


def test_public_prediction_messages_keep_frame_contract_consistent() -> None:
    if msg_adapters.PredictedRegion is None or msg_adapters.InterceptGoal is None:
        assert DEFAULT_CONTRACTS.predicted_region_wire_type == "go2_apportation_msgs/PredictedRegion"
        assert DEFAULT_CONTRACTS.intercept_goal_wire_type == "go2_apportation_msgs/InterceptGoal"
        return

    measurement = InternalTrackingMeasurement(
        frame_id="odom",
        center_xyz=(0.2, 0.3, 0.4),
        confidence=0.6,
        stamp_s=3.0,
    )
    outputs = build_conservative_prediction_outputs(
        measurement,
        measurement_age_s=0.0,
        verify_timeout_s=1.5,
        state_frame=DEFAULT_CONTRACTS.state_frame,
        predicted_region_size_xyz=(0.3, 0.3, 0.2),
        predicted_region_confidence_scale=0.5,
        predicted_region_valid_for_s=0.5,
        intercept_goal_approach_radius_m=0.35,
        intercept_goal_tolerance_m=0.15,
        intercept_goal_valid_for_s=0.5,
    )

    predicted_region = msg_adapters.build_predicted_region_msg(outputs.predicted_region)
    intercept_goal = msg_adapters.build_intercept_goal_msg(outputs.intercept_goal)

    assert predicted_region.header.frame_id == "odom"
    assert intercept_goal.header.frame_id == "odom"
    assert intercept_goal.target_pose.header.frame_id == intercept_goal.header.frame_id
    assert predicted_region.valid_for.sec == 0
    assert predicted_region.valid_for.nanosec == 500_000_000
    assert intercept_goal.valid_for.sec == 0
    assert intercept_goal.valid_for.nanosec == 500_000_000
