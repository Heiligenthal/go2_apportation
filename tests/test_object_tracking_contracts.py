from pathlib import Path

from src.go2_object_tracking.go2_object_tracking.contracts import (
    DEFAULT_CONTRACTS,
    TRACKING_STATE_LOST,
    TRACKING_STATE_OCCLUDED,
    TRACKING_STATE_REACQUIRE,
    TRACKING_STATE_VISIBLE,
)


def test_tracking_contracts_match_document_baseline() -> None:
    assert DEFAULT_CONTRACTS.state_frame == "odom"
    assert DEFAULT_CONTRACTS.internal_tracking_frame == "map"
    assert DEFAULT_CONTRACTS.tracker_rate_hz == 30.0
    assert DEFAULT_CONTRACTS.best_detection_confidence_threshold == 0.39
    assert DEFAULT_CONTRACTS.gravity_mps2 == 9.81
    assert DEFAULT_CONTRACTS.fast_input_wire_type == "go2_apportation_msgs/Detection3DArray"
    assert DEFAULT_CONTRACTS.object_state_wire_type == "go2_apportation_msgs/ObjectState"
    assert DEFAULT_CONTRACTS.throw_status_wire_type == "go2_apportation_msgs/ThrowStatus"
    assert DEFAULT_CONTRACTS.predicted_region_wire_type == "go2_apportation_msgs/PredictedRegion"
    assert DEFAULT_CONTRACTS.intercept_goal_wire_type == "go2_apportation_msgs/InterceptGoal"
    assert DEFAULT_CONTRACTS.object_state_topic == "/tracking/object_state"
    assert DEFAULT_CONTRACTS.throw_status_topic == "/tracking/throw_status"
    assert DEFAULT_CONTRACTS.predicted_region_topic == "/tracking/predicted_region"
    assert DEFAULT_CONTRACTS.intercept_goal_topic == "/tracking/intercept_goal"
    assert DEFAULT_CONTRACTS.internal_map_measurement_topic == "/tracking/internal/cube_measurement_map"


def test_tracking_state_labels_are_present() -> None:
    assert {TRACKING_STATE_VISIBLE, TRACKING_STATE_OCCLUDED, TRACKING_STATE_REACQUIRE, TRACKING_STATE_LOST} == {
        "visible",
        "occluded",
        "reacquire",
        "lost",
    }


def test_object_tracking_sources_do_not_reference_cmd_vel() -> None:
    package_root = Path("/home/unitree/go2_apportation/src/go2_object_tracking")
    for source_file in package_root.rglob("*.py"):
        assert "cmd_vel" not in source_file.read_text(encoding="utf-8")


def test_tracking_no_h06_blockers_remain_in_owner_scope() -> None:
    assert DEFAULT_CONTRACTS.blocked_by_h06_topics == ()
    assert DEFAULT_CONTRACTS.blocked_or_unclear_topics == ()


def test_tracking_public_outputs_are_ready_and_odom_led() -> None:
    assert DEFAULT_CONTRACTS.public_safe_topics == (
        "/tracking/object_state",
        "/tracking/throw_status",
        "/tracking/predicted_region",
        "/tracking/intercept_goal",
    )
    assert DEFAULT_CONTRACTS.state_frame == "odom"
