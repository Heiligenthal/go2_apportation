from src.go2_object_tracking.go2_object_tracking.contracts import DEFAULT_CONTRACTS
from src.go2_object_tracking.go2_object_tracking import msg_adapters
from src.go2_object_tracking.go2_object_tracking.msg_adapters import (
    InternalPredictionCandidate,
    InternalTrackingMeasurement,
    build_intercept_goal_msg,
    build_object_state_msg,
    build_predicted_region_msg,
    build_throw_status_msg,
)


def test_object_state_message_builder_targets_odom_with_pose_and_twist_core_fields() -> None:
    if msg_adapters.ObjectState is None:
        assert DEFAULT_CONTRACTS.object_state_wire_type == "go2_apportation_msgs/ObjectState"
        return

    message = build_object_state_msg(
        InternalTrackingMeasurement(
            frame_id="odom",
            center_xyz=(0.2, -0.1, 1.3),
            confidence=0.9,
            stamp_s=7.25,
        )
    )

    assert message.header.frame_id == "odom"
    assert message.pose.pose.position.x == 0.2
    assert message.pose.pose.position.y == -0.1
    assert message.pose.pose.position.z == 1.3
    assert message.pose.pose.orientation.w == 1.0
    assert message.twist.twist.linear.x == 0.0
    assert DEFAULT_CONTRACTS.object_state_wire_type == "go2_apportation_msgs/ObjectState"


def test_throw_status_message_builder_only_accepts_ready_public_states() -> None:
    ready_statuses = (
        "IDLE",
        "HELD",
        "RELEASE_SUSPECTED",
        "THROWN",
        "LANDED",
        "LOST",
    )

    if msg_adapters.ThrowStatus is None:
        assert DEFAULT_CONTRACTS.throw_status_wire_type == "go2_apportation_msgs/ThrowStatus"
        return

    for status in ready_statuses:
        message = build_throw_status_msg(status)
        assert message.status in (
            message.IDLE,
            message.HELD,
            message.RELEASE_SUSPECTED,
            message.THROWN,
            message.LANDED,
            message.LOST,
        )


def test_prediction_outputs_are_now_ready_public_tracking_outputs() -> None:
    assert DEFAULT_CONTRACTS.predicted_region_wire_type == "go2_apportation_msgs/PredictedRegion"
    assert DEFAULT_CONTRACTS.intercept_goal_wire_type == "go2_apportation_msgs/InterceptGoal"
    assert "/tracking/predicted_region" in DEFAULT_CONTRACTS.public_safe_topics
    assert "/tracking/intercept_goal" in DEFAULT_CONTRACTS.public_safe_topics


def test_prediction_and_intercept_builders_fill_required_fields_consistently() -> None:
    candidate = InternalPredictionCandidate(
        frame_id="odom",
        center_xyz=(0.4, -0.2, 0.9),
        confidence=0.35,
        stamp_s=4.25,
        valid_for_s=0.5,
        size_xyz=(0.3, 0.3, 0.2),
        approach_radius_m=0.35,
        goal_tolerance_m=0.15,
        is_dynamic_estimate=True,
    )

    if msg_adapters.PredictedRegion is None or msg_adapters.InterceptGoal is None:
        assert DEFAULT_CONTRACTS.predicted_region_wire_type == "go2_apportation_msgs/PredictedRegion"
        assert DEFAULT_CONTRACTS.intercept_goal_wire_type == "go2_apportation_msgs/InterceptGoal"
        return

    predicted_region = build_predicted_region_msg(candidate)
    intercept_goal = build_intercept_goal_msg(candidate)

    assert predicted_region.header.frame_id == "odom"
    assert predicted_region.center.position.x == 0.4
    assert predicted_region.center.position.y == -0.2
    assert predicted_region.center.position.z == 0.9
    assert predicted_region.size.x == 0.3
    assert predicted_region.size.y == 0.3
    assert predicted_region.size.z == 0.2
    assert predicted_region.confidence == 0.35
    assert predicted_region.valid_for.sec == 0
    assert predicted_region.valid_for.nanosec == 500_000_000

    assert intercept_goal.header.frame_id == "odom"
    assert intercept_goal.target_pose.header.frame_id == intercept_goal.header.frame_id
    assert intercept_goal.target_pose.pose.position.x == 0.4
    assert intercept_goal.target_pose.pose.position.y == -0.2
    assert intercept_goal.target_pose.pose.position.z == 0.9
    assert intercept_goal.approach_radius_m == 0.35
    assert intercept_goal.goal_tolerance_m == 0.15
    assert intercept_goal.confidence == 0.35
    assert intercept_goal.valid_for.sec == 0
    assert intercept_goal.valid_for.nanosec == 500_000_000
    assert intercept_goal.is_dynamic_estimate is True
