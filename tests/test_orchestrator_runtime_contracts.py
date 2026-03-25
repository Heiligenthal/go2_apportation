from src.go2_apportation_orchestrator.go2_apportation_orchestrator.runtime_contracts import (
    CONTROL_MODE_BALANCE_STAND,
    CONTROL_MODE_VELOCITY_MOVE,
    FRAME_BASE_LINK_NAV2,
    LEGACY_DEBUG_FRAME_ODOM_NAV2,
    STATE_CONTROL_MODE_BASELINE,
    TOPIC_BALANCE_RPY_CMD,
    TOPIC_CMD_VEL_NAV2,
    TOPIC_CONTROL_MODE_CMD,
    TOPIC_LOOK_YAW_DELTA,
    TOPIC_TRACKING_DIRECTIVE,
    TOPIC_TRACKING_INTERCEPT_GOAL,
    TRACKING_DIRECTIVE_EVENT_NAMES,
)
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_spec import (
    TransitionEvent,
    TransitionState,
)


def test_runtime_contract_topics_and_frames_are_frozen() -> None:
    assert FRAME_BASE_LINK_NAV2 == "base_link_nav2"
    assert LEGACY_DEBUG_FRAME_ODOM_NAV2 == "odom_nav2"
    assert TOPIC_CMD_VEL_NAV2 == "/cmd_vel_nav2"
    assert TOPIC_LOOK_YAW_DELTA == "/look_yaw_delta"
    assert TOPIC_BALANCE_RPY_CMD == "/balance_rpy_cmd"
    assert TOPIC_CONTROL_MODE_CMD == "/control_mode_cmd"
    assert TOPIC_TRACKING_INTERCEPT_GOAL == "/tracking/intercept_goal"
    assert TOPIC_TRACKING_DIRECTIVE == "/tracking/tracking_directive"


def test_runtime_control_mode_mapping_covers_current_frozen_states() -> None:
    assert STATE_CONTROL_MODE_BASELINE[TransitionState.INTERCEPT] == CONTROL_MODE_VELOCITY_MOVE
    assert STATE_CONTROL_MODE_BASELINE[TransitionState.SEARCH_OBJECT_LOCAL] == CONTROL_MODE_VELOCITY_MOVE
    assert STATE_CONTROL_MODE_BASELINE[TransitionState.OBSERVE_HAND] == CONTROL_MODE_BALANCE_STAND


def test_tracking_directive_events_are_parseable_without_new_runtime_logic() -> None:
    assert TRACKING_DIRECTIVE_EVENT_NAMES["REQUEST_INTERCEPT"] == "request_intercept"
    assert TransitionEvent.REQUEST_INTERCEPT.value == "request_intercept"
    assert TransitionEvent.REQUEST_LOCAL_SEARCH.value == "request_local_search"
    assert TransitionEvent.REQUEST_GLOBAL_SEARCH.value == "request_global_search"
    assert TransitionEvent.REQUEST_PICK_READY.value == "request_pick_ready"
    assert TransitionEvent.REQUEST_PICK_ABORT.value == "request_pick_abort"
