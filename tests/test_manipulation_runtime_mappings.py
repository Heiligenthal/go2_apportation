from __future__ import annotations

from src.go2_manipulation_runtime.go2_manipulation_runtime.backend_adapter import (
    BackendPickOutcome,
    BackendReleaseOutcome,
    map_backend_pick_outcome_to_result_code,
    map_backend_release_outcome_to_result_code,
)
from src.go2_manipulation_runtime.go2_manipulation_runtime.d1_reuse_points import (
    D1_REUSE_POINTS,
    LOCAL_NAMED_STATES,
)
from src.go2_manipulation_runtime.go2_manipulation_runtime.pick_result_mapping import (
    OBJECT_DROPPED,
    PICK_FAILED,
    PICK_SUCCESS,
    PICK_TIMEOUT,
    PICK_UNREACHABLE,
    SAFETY_ABORTED,
    map_pick_result_code_to_event,
)
from src.go2_manipulation_runtime.go2_manipulation_runtime.release_result_mapping import (
    RELEASE_MODE_DROP_SAFE,
    RELEASE_MODE_HANDOVER_RELEASE,
    RELEASE_MODE_OPEN_GRIPPER,
    RELEASE_RESULT_FAILED,
    RELEASE_RESULT_SAFETY_ABORTED,
    RELEASE_RESULT_SUCCESS,
    RELEASE_RESULT_TIMEOUT,
    map_release_result_to_mission_result,
)


def test_pick_result_code_mapping_matches_freeze() -> None:
    assert map_pick_result_code_to_event(PICK_SUCCESS).event_label == "grasp_ok"
    assert map_pick_result_code_to_event(PICK_FAILED).event_label == "grasp_failed"
    assert map_pick_result_code_to_event(OBJECT_DROPPED).event_label == "object_dropped"
    assert map_pick_result_code_to_event(PICK_UNREACHABLE).event_label == "object_unreachable"
    assert map_pick_result_code_to_event(PICK_TIMEOUT).event_label == "timeout"
    assert map_pick_result_code_to_event(SAFETY_ABORTED).event_label == "safety_abort"


def test_release_mapping_matches_freeze() -> None:
    assert (
        map_release_result_to_mission_result(
            RELEASE_MODE_HANDOVER_RELEASE,
            RELEASE_RESULT_SUCCESS,
        ).mission_result
        == "HANDOVER_RELEASE_SUCCESS"
    )
    assert (
        map_release_result_to_mission_result(
            RELEASE_MODE_DROP_SAFE,
            RELEASE_RESULT_SUCCESS,
        ).mission_result
        == "DROP_RELEASE_SUCCESS"
    )
    assert (
        map_release_result_to_mission_result(
            RELEASE_MODE_OPEN_GRIPPER,
            RELEASE_RESULT_TIMEOUT,
        ).mission_result
        == "RELEASE_TIMEOUT"
    )
    assert (
        map_release_result_to_mission_result(
            RELEASE_MODE_OPEN_GRIPPER,
            RELEASE_RESULT_SAFETY_ABORTED,
        ).mission_result
        == "SAFETY_ABORTED"
    )
    assert (
        map_release_result_to_mission_result(
            RELEASE_MODE_OPEN_GRIPPER,
            RELEASE_RESULT_FAILED,
        ).mission_result
        == "RELEASE_FAILED"
    )


def test_d1_reuse_points_keep_existing_stack_as_primary_backend() -> None:
    assert D1_REUSE_POINTS.arm_group == "arm"
    assert D1_REUSE_POINTS.gripper_group == "gripper"
    assert D1_REUSE_POINTS.arm_controller_action == "/d1_550_arm_controller/follow_joint_trajectory"
    assert D1_REUSE_POINTS.gripper_controller_action == "/d1_550_gripper_controller/follow_joint_trajectory"
    assert LOCAL_NAMED_STATES == ("home", "ready", "stow", "open", "closed")


def test_backend_pick_adapter_stays_separate_from_normative_mapping() -> None:
    assert map_backend_pick_outcome_to_result_code(BackendPickOutcome(success=True)) == PICK_SUCCESS
    assert map_backend_pick_outcome_to_result_code(BackendPickOutcome(dropped=True)) == OBJECT_DROPPED
    assert (
        map_backend_pick_outcome_to_result_code(BackendPickOutcome(unreachable=True))
        == PICK_UNREACHABLE
    )
    assert map_backend_pick_outcome_to_result_code(BackendPickOutcome(timeout=True)) == PICK_TIMEOUT
    assert (
        map_backend_pick_outcome_to_result_code(BackendPickOutcome(safety_aborted=True))
        == SAFETY_ABORTED
    )


def test_backend_release_adapter_stays_separate_from_mission_mapping() -> None:
    assert map_backend_release_outcome_to_result_code(BackendReleaseOutcome(success=True)) == RELEASE_RESULT_SUCCESS
    assert map_backend_release_outcome_to_result_code(BackendReleaseOutcome(timeout=True)) == RELEASE_RESULT_TIMEOUT
    assert (
        map_backend_release_outcome_to_result_code(BackendReleaseOutcome(safety_aborted=True))
        == RELEASE_RESULT_SAFETY_ABORTED
    )
    assert map_backend_release_outcome_to_result_code(BackendReleaseOutcome()) == RELEASE_RESULT_FAILED
