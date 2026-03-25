from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


NO_GUARD_TOKEN = "--"
NO_ACTION_TOKEN = "--"
NO_TIMEOUT_KEY = "--"


class TransitionState(str, Enum):
    ANY = "ANY"
    IDLE = "IDLE"
    SEARCH_PERSON = "SEARCH_PERSON"
    APPROACH_PERSON = "APPROACH_PERSON"
    OBSERVE_HAND = "OBSERVE_HAND"
    TRACK_THROWN = "TRACK_THROWN"
    SEARCH_OBJECT_LOCAL = "SEARCH_OBJECT_LOCAL"
    SEARCH_OBJECT_GLOBAL = "SEARCH_OBJECT_GLOBAL"
    INTERCEPT = "INTERCEPT"
    PICK = "PICK"
    RETURN_TO_PERSON = "RETURN_TO_PERSON"
    HOLD_AND_FOLLOW = "HOLD_AND_FOLLOW"
    HANDOVER_RELEASE = "HANDOVER_RELEASE"
    INTERRUPTED = "INTERRUPTED"
    FAILSAFE_ABORT = "FAILSAFE_ABORT"


class TransitionEvent(str, Enum):
    VC_LETS_PLAY = "vc_lets_play"
    VC_SEARCH = "vc_search"
    VC_RELEASE = "vc_release"
    VC_ABORT = "vc_abort"
    VC_PAUSE = "vc_pause"
    VC_RESUME = "vc_resume"
    PERSON_DETECTED = "person_detected"
    PERSON_LOST = "person_lost"
    OBJECT_DETECTED = "object_detected"
    OBJECT_LOST = "object_lost"
    THROW_SUSPECTED = "throw_suspected"
    THROW_CONFIRMED = "throw_confirmed"
    REQUEST_INTERCEPT = "request_intercept"
    REQUEST_LOCAL_SEARCH = "request_local_search"
    REQUEST_GLOBAL_SEARCH = "request_global_search"
    REQUEST_PICK_READY = "request_pick_ready"
    REQUEST_PICK_ABORT = "request_pick_abort"
    APPROACH_REACHED = "approach_reached"
    INTERCEPT_REACHED = "intercept_reached"
    NAV_FAILED = "nav_failed"
    OBJECT_UNREACHABLE = "object_unreachable"
    GRASP_OK = "grasp_ok"
    GRASP_FAILED = "grasp_failed"
    OBJECT_DROPPED = "object_dropped"
    E_STOP = "e_stop"
    TIMEOUT = "timeout"
    LOCALIZATION_LOST = "localization_lost"
    BATTERY_LOW = "battery_low"
    MANUAL_OVERRIDE_ACTIVE = "MANUAL_OVERRIDE_ACTIVE"
    MANUAL_OVERRIDE_RELEASED = "MANUAL_OVERRIDE_RELEASED"


class PriorityGroup(str, Enum):
    ANY_STATE_SAFETY = "any_state_safety"
    ANY_STATE_INTERRUPT = "any_state_interrupt"
    ANY_STATE_OPERATOR = "any_state_operator"
    MODE_AND_PERSON = "mode_and_person"
    PLAY_FLOW = "play_flow"
    SEARCH_FLOW = "search_flow"
    INTERCEPT_PICK_RETURN_FOLLOW_RELEASE = "intercept_pick_return_follow_release"


@dataclass(frozen=True)
class TransitionRow:
    """Static mirror row from Document 002 transition tables."""

    source_table: str
    priority_group: PriorityGroup
    from_state: TransitionState
    event: TransitionEvent
    guard_expr: str
    guard_tokens: tuple[str, ...]
    action_expr: str
    action_tokens: tuple[str, ...]
    to_state: TransitionState
    timeout_key: str
    notes: str = ""


@dataclass(frozen=True)
class StateActionRow:
    """Static mirror row from Document 002 state-actions table."""

    state: TransitionState
    entry_tokens: tuple[str, ...]
    do_tokens: tuple[str, ...]
    exit_tokens: tuple[str, ...]


@dataclass(frozen=True)
class StaticIssue:
    code: str
    message: str


TIMEOUT_PARAMETER_KEYS: tuple[str, ...] = (
    "t_search_person",
    "t_approach",
    "t_observe",
    "t_track",
    "t_local",
    "t_global",
    "t_intercept",
    "t_pick",
    "t_return",
    "t_follow",
    "t_handover",
)

RETRY_PARAMETER_KEYS: tuple[str, ...] = ("k_nav", "pick_retries")

# Used by transitions but currently not listed in the parameter baseline table.
TIMEOUT_KEYS_TODO_STUB: tuple[str, ...] = ("t_handover",)

GUARD_TOKENS_TODO_STUB: tuple[str, ...] = (
    "MODE=PLAY",
    "MODE=SEARCH",
    "MODE=PLAY & throw_confirmed",
    "retries<2",
    "retries>=2",
)

ACTION_TOKENS_TODO_STUB: tuple[str, ...] = (
    "retry_nav(k++)",
    "if k>k_nav then abort",
    "retry_pick(r++)",
    "adjust_pose()",
    "start_pick(object_pose)",
    "release()",
)


TRANSITIONS_ANY_STATE: list[TransitionRow] = [
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_SAFETY,
        from_state=TransitionState.ANY,
        event=TransitionEvent.E_STOP,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="stop_motion(), arm_safe()",
        action_tokens=("stop_motion()", "arm_safe()"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
        notes="sofort",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_SAFETY,
        from_state=TransitionState.ANY,
        event=TransitionEvent.BATTERY_LOW,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="stop_motion(), arm_safe()",
        action_tokens=("stop_motion()", "arm_safe()"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
        notes="sofort",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_SAFETY,
        from_state=TransitionState.ANY,
        event=TransitionEvent.LOCALIZATION_LOST,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="stop_motion(), arm_safe()",
        action_tokens=("stop_motion()", "arm_safe()"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
        notes="sofort",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_INTERRUPT,
        from_state=TransitionState.ANY,
        event=TransitionEvent.MANUAL_OVERRIDE_ACTIVE,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_cancel(); mark_interrupted()",
        action_tokens=("nav_cancel()", "mark_interrupted()"),
        to_state=TransitionState.INTERRUPTED,
        timeout_key=NO_TIMEOUT_KEY,
        notes="Teleop/Mux takeover",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_INTERRUPT,
        from_state=TransitionState.INTERRUPTED,
        event=TransitionEvent.MANUAL_OVERRIDE_RELEASED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="hold_position(); wait_explicit_resume()",
        action_tokens=("hold_position()", "wait_explicit_resume()"),
        to_state=TransitionState.INTERRUPTED,
        timeout_key=NO_TIMEOUT_KEY,
        notes="no auto-resume",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_OPERATOR,
        from_state=TransitionState.ANY,
        event=TransitionEvent.VC_ABORT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_cancel(); pick_cancel(); reset_mission_context(); arm_safe()",
        action_tokens=("nav_cancel()", "pick_cancel()", "reset_mission_context()", "arm_safe()"),
        to_state=TransitionState.IDLE,
        timeout_key=NO_TIMEOUT_KEY,
        notes="Operator hard abort",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_OPERATOR,
        from_state=TransitionState.ANY,
        event=TransitionEvent.VC_PAUSE,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_cancel(), hold_position()",
        action_tokens=("nav_cancel()", "hold_position()"),
        to_state=TransitionState.IDLE,
        timeout_key=NO_TIMEOUT_KEY,
        notes="optional Pause-State",
    ),
    TransitionRow(
        source_table="globale_any_state_regeln",
        priority_group=PriorityGroup.ANY_STATE_OPERATOR,
        from_state=TransitionState.IDLE,
        event=TransitionEvent.VC_RESUME,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr=NO_ACTION_TOKEN,
        action_tokens=(NO_ACTION_TOKEN,),
        to_state=TransitionState.IDLE,
        timeout_key=NO_TIMEOUT_KEY,
        notes="no-op (placeholder)",
    ),
]


TRANSITIONS_MODE_AND_PERSON: list[TransitionRow] = [
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.IDLE,
        event=TransitionEvent.VC_LETS_PLAY,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_mode(PLAY); reset_counters()",
        action_tokens=("set_mode(PLAY)", "reset_counters()"),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.IDLE,
        event=TransitionEvent.VC_SEARCH,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_mode(SEARCH); reset_counters()",
        action_tokens=("set_mode(SEARCH)", "reset_counters()"),
        to_state=TransitionState.SEARCH_OBJECT_GLOBAL,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.SEARCH_PERSON,
        event=TransitionEvent.PERSON_DETECTED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_person_target(); nav_goal(person+offset)",
        action_tokens=("set_person_target()", "nav_goal(person+offset)"),
        to_state=TransitionState.APPROACH_PERSON,
        timeout_key="t_search_person",
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.SEARCH_PERSON,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="voice_prompt(optional); stop_motion()",
        action_tokens=("voice_prompt(optional)", "stop_motion()"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.APPROACH_PERSON,
        event=TransitionEvent.APPROACH_REACHED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="stabilize(); set_last_seen(person)",
        action_tokens=("stabilize()", "set_last_seen(person)"),
        to_state=TransitionState.OBSERVE_HAND,
        timeout_key="t_approach",
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.APPROACH_PERSON,
        event=TransitionEvent.NAV_FAILED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="retry_nav(k++); if k>k_nav then abort",
        action_tokens=("retry_nav(k++)", "if k>k_nav then abort"),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key="t_approach",
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.OBSERVE_HAND,
        event=TransitionEvent.PERSON_LOST,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_last_seen(person); nav_cancel()",
        action_tokens=("set_last_seen(person)", "nav_cancel()"),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key="t_observe",
    ),
    TransitionRow(
        source_table="mode_einstieg_und_person_handling",
        priority_group=PriorityGroup.MODE_AND_PERSON,
        from_state=TransitionState.OBSERVE_HAND,
        event=TransitionEvent.TIMEOUT,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="voice_prompt(optional)",
        action_tokens=("voice_prompt(optional)",),
        to_state=TransitionState.OBSERVE_HAND,
        timeout_key="t_observe",
    ),
]


TRANSITIONS_PLAY_FLOW: list[TransitionRow] = [
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.OBSERVE_HAND,
        event=TransitionEvent.OBJECT_DETECTED,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="track_hand_scene(); set_object_last_seen()",
        action_tokens=("track_hand_scene()", "set_object_last_seen()"),
        to_state=TransitionState.OBSERVE_HAND,
        timeout_key="t_observe",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.OBSERVE_HAND,
        event=TransitionEvent.THROW_SUSPECTED,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="start_track()",
        action_tokens=("start_track()",),
        to_state=TransitionState.TRACK_THROWN,
        timeout_key="t_track",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.OBSERVE_HAND,
        event=TransitionEvent.VC_SEARCH,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="init_local_search(center=person_last_seen)",
        action_tokens=("init_local_search(center=person_last_seen)",),
        to_state=TransitionState.SEARCH_OBJECT_LOCAL,
        timeout_key="t_local",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.TRACK_THROWN,
        event=TransitionEvent.THROW_CONFIRMED,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="predict_region(); nav_goal(intercept_goal)",
        action_tokens=("predict_region()", "nav_goal(intercept_goal)"),
        to_state=TransitionState.INTERCEPT,
        timeout_key="t_intercept",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.TRACK_THROWN,
        event=TransitionEvent.OBJECT_LOST,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="init_local_search(center=object_last_seen)",
        action_tokens=("init_local_search(center=object_last_seen)",),
        to_state=TransitionState.SEARCH_OBJECT_LOCAL,
        timeout_key="t_local",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.TRACK_THROWN,
        event=TransitionEvent.TIMEOUT,
        guard_expr="MODE=PLAY",
        guard_tokens=("MODE=PLAY",),
        action_expr="init_local_search(center=object_last_seen)",
        action_tokens=("init_local_search(center=object_last_seen)",),
        to_state=TransitionState.SEARCH_OBJECT_LOCAL,
        timeout_key="t_local",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.SEARCH_OBJECT_LOCAL,
        event=TransitionEvent.OBJECT_DETECTED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_goal(object_pose)",
        action_tokens=("nav_goal(object_pose)",),
        to_state=TransitionState.INTERCEPT,
        timeout_key="t_intercept",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.SEARCH_OBJECT_LOCAL,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="init_global_search()",
        action_tokens=("init_global_search()",),
        to_state=TransitionState.SEARCH_OBJECT_GLOBAL,
        timeout_key="t_global",
    ),
    TransitionRow(
        source_table="play_flow_throw_track_local_search",
        priority_group=PriorityGroup.PLAY_FLOW,
        from_state=TransitionState.SEARCH_OBJECT_LOCAL,
        event=TransitionEvent.VC_LETS_PLAY,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_cancel(); set_mode(PLAY)",
        action_tokens=("nav_cancel()", "set_mode(PLAY)"),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key=NO_TIMEOUT_KEY,
    ),
]


TRANSITIONS_SEARCH_FLOW: list[TransitionRow] = [
    TransitionRow(
        source_table="search_flow_global_search",
        priority_group=PriorityGroup.SEARCH_FLOW,
        from_state=TransitionState.SEARCH_OBJECT_GLOBAL,
        event=TransitionEvent.OBJECT_DETECTED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_goal(object_pose)",
        action_tokens=("nav_goal(object_pose)",),
        to_state=TransitionState.INTERCEPT,
        timeout_key="t_intercept",
    ),
    TransitionRow(
        source_table="search_flow_global_search",
        priority_group=PriorityGroup.SEARCH_FLOW,
        from_state=TransitionState.SEARCH_OBJECT_GLOBAL,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="voice_prompt(optional); stop_motion()",
        action_tokens=("voice_prompt(optional)", "stop_motion()"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="search_flow_global_search",
        priority_group=PriorityGroup.SEARCH_FLOW,
        from_state=TransitionState.SEARCH_OBJECT_GLOBAL,
        event=TransitionEvent.VC_LETS_PLAY,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_mode(PLAY)",
        action_tokens=("set_mode(PLAY)",),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key=NO_TIMEOUT_KEY,
    ),
]


TRANSITIONS_INTERCEPT_PICK_RETURN_FOLLOW_RELEASE: list[TransitionRow] = [
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.INTERCEPT,
        event=TransitionEvent.INTERCEPT_REACHED,
        guard_expr="MODE=PLAY & throw_confirmed",
        guard_tokens=("MODE=PLAY", "throw_confirmed"),
        action_expr="start_pick(object_pose)",
        action_tokens=("start_pick(object_pose)",),
        to_state=TransitionState.PICK,
        timeout_key="t_pick",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.INTERCEPT,
        event=TransitionEvent.INTERCEPT_REACHED,
        guard_expr="MODE=SEARCH",
        guard_tokens=("MODE=SEARCH",),
        action_expr="start_pick(object_pose)",
        action_tokens=("start_pick(object_pose)",),
        to_state=TransitionState.PICK,
        timeout_key="t_pick",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.INTERCEPT,
        event=TransitionEvent.OBJECT_LOST,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="init_local_search(center=object_last_seen)",
        action_tokens=("init_local_search(center=object_last_seen)",),
        to_state=TransitionState.SEARCH_OBJECT_LOCAL,
        timeout_key="t_local",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.INTERCEPT,
        event=TransitionEvent.NAV_FAILED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="retry_nav(k++); if k>k_nav then abort",
        action_tokens=("retry_nav(k++)", "if k>k_nav then abort"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.INTERCEPT,
        event=TransitionEvent.OBJECT_UNREACHABLE,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="voice_prompt(optional)",
        action_tokens=("voice_prompt(optional)",),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.PICK,
        event=TransitionEvent.GRASP_OK,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_carry(true); ensure_arm_carry_pose()",
        action_tokens=("set_carry(true)", "ensure_arm_carry_pose()"),
        to_state=TransitionState.RETURN_TO_PERSON,
        timeout_key="t_return",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.PICK,
        event=TransitionEvent.GRASP_FAILED,
        guard_expr="retries<2",
        guard_tokens=("retries<2",),
        action_expr="retry_pick(r++); adjust_pose()",
        action_tokens=("retry_pick(r++)", "adjust_pose()"),
        to_state=TransitionState.PICK,
        timeout_key="t_pick",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.PICK,
        event=TransitionEvent.GRASP_FAILED,
        guard_expr="retries>=2",
        guard_tokens=("retries>=2",),
        action_expr="voice_prompt(optional); arm_safe()",
        action_tokens=("voice_prompt(optional)", "arm_safe()"),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.PICK,
        event=TransitionEvent.OBJECT_DROPPED,
        guard_expr="retries<2",
        guard_tokens=("retries<2",),
        action_expr="retry_pick(r++)",
        action_tokens=("retry_pick(r++)",),
        to_state=TransitionState.PICK,
        timeout_key="t_pick",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.PICK,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="arm_safe()",
        action_tokens=("arm_safe()",),
        to_state=TransitionState.FAILSAFE_ABORT,
        timeout_key=NO_TIMEOUT_KEY,
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.RETURN_TO_PERSON,
        event=TransitionEvent.PERSON_DETECTED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_goal(person+offset)",
        action_tokens=("nav_goal(person+offset)",),
        to_state=TransitionState.RETURN_TO_PERSON,
        timeout_key="t_return",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.RETURN_TO_PERSON,
        event=TransitionEvent.APPROACH_REACHED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="stop_motion()",
        action_tokens=("stop_motion()",),
        to_state=TransitionState.HOLD_AND_FOLLOW,
        timeout_key="t_follow",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.RETURN_TO_PERSON,
        event=TransitionEvent.NAV_FAILED,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="set_last_seen(person)",
        action_tokens=("set_last_seen(person)",),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key="t_search_person",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.RETURN_TO_PERSON,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="SEARCH_PERSON",
        action_tokens=("SEARCH_PERSON",),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key="t_search_person",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.HOLD_AND_FOLLOW,
        event=TransitionEvent.VC_RELEASE,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="release(); arm_safe()",
        action_tokens=("release()", "arm_safe()"),
        to_state=TransitionState.HANDOVER_RELEASE,
        timeout_key="t_handover",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.HOLD_AND_FOLLOW,
        event=TransitionEvent.PERSON_LOST,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="nav_cancel(); set_last_seen(person)",
        action_tokens=("nav_cancel()", "set_last_seen(person)"),
        to_state=TransitionState.SEARCH_PERSON,
        timeout_key="t_search_person",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.HOLD_AND_FOLLOW,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr="voice_prompt(optional)",
        action_tokens=("voice_prompt(optional)",),
        to_state=TransitionState.HOLD_AND_FOLLOW,
        timeout_key="t_follow",
    ),
    TransitionRow(
        source_table="interception_pick_return_follow_release",
        priority_group=PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
        from_state=TransitionState.HANDOVER_RELEASE,
        event=TransitionEvent.TIMEOUT,
        guard_expr=NO_GUARD_TOKEN,
        guard_tokens=(NO_GUARD_TOKEN,),
        action_expr=NO_ACTION_TOKEN,
        action_tokens=(NO_ACTION_TOKEN,),
        to_state=TransitionState.OBSERVE_HAND,
        timeout_key=NO_TIMEOUT_KEY,
    ),
]


TRANSITIONS_BASELINE: list[TransitionRow] = [
    *TRANSITIONS_ANY_STATE,
    *TRANSITIONS_MODE_AND_PERSON,
    *TRANSITIONS_PLAY_FLOW,
    *TRANSITIONS_SEARCH_FLOW,
    *TRANSITIONS_INTERCEPT_PICK_RETURN_FOLLOW_RELEASE,
]


STATE_ACTIONS_BASELINE: list[StateActionRow] = [
    StateActionRow(
        state=TransitionState.IDLE,
        entry_tokens=("arm_safe()", "nav_cancel()", "reset_volatile_state()"),
        do_tokens=(
            "subscribe /voice/command",
            "emit events vc_lets_play/vc_search/vc_abort/vc_pause",
            "guard health: battery/localization ok",
        ),
        exit_tokens=("latch mode (PLAY/SEARCH) in blackboard",),
    ),
    StateActionRow(
        state=TransitionState.SEARCH_PERSON,
        entry_tokens=("set_search_seed(person_last_seen or global)", "start_scan_behavior(optional)"),
        do_tokens=(
            "run person perception (topic-driven)",
            "if person_detected: set person target + offset",
            "optionally rotate in place / waypoint loop (Budget: t_search_person)",
        ),
        exit_tokens=("stop_scan_behavior()",),
    ),
    StateActionRow(
        state=TransitionState.APPROACH_PERSON,
        entry_tokens=("compute approach pose: person_pose + offset", "nav_goal(/navigate_to_pose)"),
        do_tokens=(
            "monitor Nav2 feedback/result",
            "update goal if person_pose changes significantly (optional)",
            "if nav_failed: retry budget k_nav",
        ),
        exit_tokens=("nav_cancel() on transition to non-nav states", "stabilize() (short settle, e.g. 0.5s)"),
    ),
    StateActionRow(
        state=TransitionState.OBSERVE_HAND,
        entry_tokens=("set_context(hand_scene)", "clear throw state machine"),
        do_tokens=(
            "keep person in view: update base heading via small nav goals (optional)",
            "run object-in-hand detection; update object_last_seen",
            "run throw detector: emits throw_suspected/confirmed",
            "operator override: on vc_search start local search",
        ),
        exit_tokens=("stop any observe-specific behaviors",),
    ),
    StateActionRow(
        state=TransitionState.TRACK_THROWN,
        entry_tokens=("init tracker (Kalman/IMM)", "freeze person tracking (store last_seen)"),
        do_tokens=(
            "update object state (pose/vel/cov)",
            "maintain object in FOV by yaw/reposition goals",
            "on throw_confirmed: compute intercept region/pose",
            "if lost: emit object_lost to trigger local search",
        ),
        exit_tokens=("stop tracker timers",),
    ),
    StateActionRow(
        state=TransitionState.SEARCH_OBJECT_LOCAL,
        entry_tokens=(
            "init local search pattern: center=person_last_seen or object_last_seen",
            "set search budget t_local",
        ),
        do_tokens=(
            "execute local pattern: rotate + radial/sector sweeps",
            "run object detector/tracker",
            "if object_detected: latch pose and go INTERCEPT",
            "if timeout: fallback to global search",
        ),
        exit_tokens=("stop local search pattern",),
    ),
    StateActionRow(
        state=TransitionState.SEARCH_OBJECT_GLOBAL,
        entry_tokens=("init waypoint route / exploration plan", "set budget t_global"),
        do_tokens=(
            "follow waypoints (/follow_waypoints)",
            "continuously run object detector",
            "on object_detected: cancel waypoints, go INTERCEPT",
            "on timeout: FAILSAFE_ABORT",
        ),
        exit_tokens=("cancel waypoint action if active",),
    ),
    StateActionRow(
        state=TransitionState.INTERCEPT,
        entry_tokens=("compute intercept goal pose (predicted region or object pose)", "nav_goal(/navigate_to_pose)"),
        do_tokens=(
            "update goal if object pose updates (optional, rate-limited)",
            "if object_lost: go local search",
            "on intercept_reached: evaluate PICK guard (mode dependent)",
            "detect unreachable/nav_failed and abort per table",
        ),
        exit_tokens=("nav_cancel()", "stabilize() before pick (short settle)"),
    ),
    StateActionRow(
        state=TransitionState.PICK,
        entry_tokens=("lock target pose snapshot (PoseStamped + frame)", "start manipulation action /manipulation/pick"),
        do_tokens=(
            "monitor pick action feedback/result",
            "on grasp_failed/object_dropped: retry up to 2",
            "on grasp_ok: set carry pose + proceed return",
        ),
        exit_tokens=("ensure carry pose or safe pose depending on outcome",),
    ),
    StateActionRow(
        state=TransitionState.RETURN_TO_PERSON,
        entry_tokens=("if person visible: nav_goal(person+offset)", "else: go SEARCH_PERSON or nav to last_seen"),
        do_tokens=(
            "update person goal periodically (rate-limited)",
            "if nav fails: fallback to SEARCH_PERSON",
            "on approach_reached: transition to HOLD_AND_FOLLOW",
        ),
        exit_tokens=("nav_cancel()",),
    ),
    StateActionRow(
        state=TransitionState.HOLD_AND_FOLLOW,
        entry_tokens=("set follow offset (e.g. 1.0m in front/behind)", "start periodic nav goal updates"),
        do_tokens=(
            "continuously update goal = person_pose + offset (Nav2)",
            "maintain arm offer posture",
            "wait for vc_release",
            "if person lost: SEARCH_PERSON",
        ),
        exit_tokens=("nav_cancel()", "stop periodic updates"),
    ),
    StateActionRow(
        state=TransitionState.HANDOVER_RELEASE,
        entry_tokens=("call release (/manipulation/release)", "arm_safe()"),
        do_tokens=("verify release complete", "optional: confirm operator took object"),
        exit_tokens=("transition to OBSERVE_HAND (PLAY) or IDLE (SEARCH)",),
    ),
    StateActionRow(
        state=TransitionState.INTERRUPTED,
        entry_tokens=("nav_cancel()", "hold_position()", "mark interrupted cause (manual override)"),
        do_tokens=(
            "wait for explicit operator/orchestrator resume rule",
            "monitor manual override status (MANUAL_OVERRIDE_RELEASED)",
            "do not auto-resume mission on release event",
        ),
        exit_tokens=("clear interrupted latch only on explicit resume/new command",),
    ),
    StateActionRow(
        state=TransitionState.FAILSAFE_ABORT,
        entry_tokens=("stop_motion()", "nav_cancel()", "arm_safe()", "optional voice prompt"),
        do_tokens=("wait for operator command (vc_abort/manual reset)", "system health monitoring"),
        exit_tokens=("on reset: go IDLE",),
    ),
]


STATE_ACTIONS_BY_STATE: dict[TransitionState, StateActionRow] = {
    row.state: row for row in STATE_ACTIONS_BASELINE
}


def collect_static_issues() -> tuple[StaticIssue, ...]:
    """Static checks only: no engine, no guards/actions execution."""

    issues: list[StaticIssue] = []

    expected_size = (
        len(TRANSITIONS_ANY_STATE)
        + len(TRANSITIONS_MODE_AND_PERSON)
        + len(TRANSITIONS_PLAY_FLOW)
        + len(TRANSITIONS_SEARCH_FLOW)
        + len(TRANSITIONS_INTERCEPT_PICK_RETURN_FOLLOW_RELEASE)
    )
    if len(TRANSITIONS_BASELINE) != expected_size:
        issues.append(
            StaticIssue(
                code="MERGE_MISMATCH",
                message=(
                    "TRANSITIONS_BASELINE size mismatch. "
                    f"expected {expected_size}, got {len(TRANSITIONS_BASELINE)}"
                ),
            )
        )

    seen: set[tuple[str, str, str, str, str, str]] = set()
    for row in TRANSITIONS_BASELINE:
        signature = (
            row.source_table,
            row.from_state.value,
            row.event.value,
            row.guard_expr,
            row.to_state.value,
            row.timeout_key,
        )
        if signature in seen:
            issues.append(
                StaticIssue(
                    code="DUPLICATE_TRANSITION",
                    message=f"Duplicate transition row in {row.source_table}: {signature}",
                )
            )
        seen.add(signature)

    used_timeout_keys = {
        row.timeout_key for row in TRANSITIONS_BASELINE if row.timeout_key != NO_TIMEOUT_KEY
    }
    declared_timeout_keys = set(TIMEOUT_PARAMETER_KEYS)
    missing_timeout_keys = sorted(used_timeout_keys - declared_timeout_keys)
    for timeout_key in missing_timeout_keys:
        issues.append(
            StaticIssue(
                code="TIMEOUT_KEY_UNDECLARED",
                message=(
                    f"Transition timeout key '{timeout_key}' is used but not listed in "
                    "the baseline parameter table."
                ),
            )
        )

    for stub_timeout_key in TIMEOUT_KEYS_TODO_STUB:
        if stub_timeout_key not in used_timeout_keys:
            issues.append(
                StaticIssue(
                    code="TODO_TIMEOUT_UNUSED",
                    message=f"Configured TODO timeout key '{stub_timeout_key}' is not used.",
                )
            )

    expected_interrupt_pairs = {
        (
            TransitionState.ANY,
            TransitionEvent.MANUAL_OVERRIDE_ACTIVE,
            TransitionState.INTERRUPTED,
        ),
        (
            TransitionState.INTERRUPTED,
            TransitionEvent.MANUAL_OVERRIDE_RELEASED,
            TransitionState.INTERRUPTED,
        ),
    }
    observed_interrupt_pairs = {
        (row.from_state, row.event, row.to_state)
        for row in TRANSITIONS_ANY_STATE
        if row.priority_group == PriorityGroup.ANY_STATE_INTERRUPT
    }
    if expected_interrupt_pairs != observed_interrupt_pairs:
        issues.append(
            StaticIssue(
                code="Q007_INTERRUPT_RULES_INCOMPLETE",
                message=(
                    "Any-state interrupt rules do not match Q007 baseline "
                    "(MANUAL_OVERRIDE_ACTIVE/RELEASED with INTERRUPTED)."
                ),
            )
        )

    states_in_transitions = {
        row.from_state for row in TRANSITIONS_BASELINE if row.from_state != TransitionState.ANY
    } | {row.to_state for row in TRANSITIONS_BASELINE if row.to_state != TransitionState.ANY}
    missing_state_actions = sorted(
        state.value for state in states_in_transitions if state not in STATE_ACTIONS_BY_STATE
    )
    if missing_state_actions:
        issues.append(
            StaticIssue(
                code="STATE_ACTIONS_MISSING",
                message=f"States without StateActionRow: {', '.join(missing_state_actions)}",
            )
        )

    return tuple(issues)
