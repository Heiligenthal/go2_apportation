from __future__ import annotations

import importlib.util

import pytest

NAV2_AVAILABLE = importlib.util.find_spec("nav2_msgs") is not None

pytestmark = [
    pytest.mark.nav2,
    pytest.mark.skipif(
        not NAV2_AVAILABLE,
        reason="nav2_msgs not available in this environment (baseline ros-base)",
    ),
]

if NAV2_AVAILABLE:
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.orchestrator_runtime_core import (
        OrchestratorCore,
        parse_transition_event,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.manipulation_skill_stub import (
        ManipulationSkillStub,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.skill_bundle import (
        SkillBundle,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_spec import (
        TransitionEvent,
        TransitionState,
    )
else:
    class _TransitionEventPlaceholder:
        VC_LETS_PLAY = "vc_lets_play"
        MANUAL_OVERRIDE_ACTIVE = "MANUAL_OVERRIDE_ACTIVE"

    class _TransitionStatePlaceholder:
        IDLE = "IDLE"
        OBSERVE_HAND = "OBSERVE_HAND"
        PICK = "PICK"

    TransitionEvent = _TransitionEventPlaceholder
    TransitionState = _TransitionStatePlaceholder


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("vc_lets_play", TransitionEvent.VC_LETS_PLAY),
        ("VC_LETS_PLAY", TransitionEvent.VC_LETS_PLAY),
        ("MANUAL_OVERRIDE_ACTIVE", TransitionEvent.MANUAL_OVERRIDE_ACTIVE),
        ("manual_override_active", TransitionEvent.MANUAL_OVERRIDE_ACTIVE),
    ],
)
def test_parse_transition_event_mapping(raw: str, expected: TransitionEvent) -> None:
    assert parse_transition_event(raw) == expected


def test_parse_transition_event_unknown() -> None:
    assert parse_transition_event("not_an_event") is None


def test_core_step_applies_transition_without_ros() -> None:
    core = OrchestratorCore(initial_state=TransitionState.IDLE)

    status = core.step("vc_lets_play")

    assert core.current_state == TransitionState.SEARCH_PERSON
    assert core.context_snapshot.mode == "PLAY"
    assert status["result"] == "transition_applied"
    assert status["last_event"] == TransitionEvent.VC_LETS_PLAY.value
    assert status["chosen_transition_summary"] == "IDLE --vc_lets_play--> SEARCH_PERSON"
    assert status["last_transition_summary"] == "IDLE --vc_lets_play--> SEARCH_PERSON"
    assert status["active_backend"] == "stub"
    assert status["last_dispatched_actions_count"] == 0
    assert status["last_unhandled_tokens_count"] == 2
    assert "set_mode(PLAY)" in status["last_unhandled_tokens"]


def test_core_manual_override_forces_interrupted() -> None:
    core = OrchestratorCore(initial_state=TransitionState.SEARCH_PERSON)

    status = core.step("MANUAL_OVERRIDE_ACTIVE")

    assert core.current_state == TransitionState.INTERRUPTED
    assert core.context_snapshot.manual_override_active is True
    assert status["result"] == "transition_applied"
    assert status["state"] == TransitionState.INTERRUPTED.value


def test_core_dispatches_action_tokens_to_skill_history() -> None:
    core = OrchestratorCore(initial_state=TransitionState.SEARCH_OBJECT_GLOBAL)

    status = core.step("object_detected")

    assert core.current_state == TransitionState.INTERCEPT
    assert status["result"] == "transition_applied"
    assert status["last_dispatched_actions_count"] == 1
    assert status["last_unhandled_tokens_count"] == 0
    assert status["last_unhandled_tokens"] == ()
    assert len(core.skills.nav2.history) == 1
    assert core.skills.nav2.history[0]["request"] == "navigate"
    assert status["last_skill_history_sizes"]["nav2_history_len"] == 1
    assert status["last_skill_history_sizes"]["manip_history_len"] == 0


def test_core_status_exposes_unhandled_tokens_for_transition_actions() -> None:
    core = OrchestratorCore(initial_state=TransitionState.IDLE)

    status = core.step("vc_lets_play")

    assert status["result"] == "transition_applied"
    assert status["last_unhandled_tokens_count"] == 2
    assert "set_mode(PLAY)" in status["last_unhandled_tokens"]
    assert "reset_counters()" in status["last_unhandled_tokens"]


def test_core_interrupted_policy_blocks_non_allowed_events() -> None:
    core = OrchestratorCore(initial_state=TransitionState.INTERRUPTED)

    status = core.step("object_detected")

    assert core.current_state == TransitionState.INTERRUPTED
    assert status["result"] == "policy_blocked"


def test_core_vc_abort_transitions_to_idle_and_resets_context() -> None:
    core = OrchestratorCore(initial_state=TransitionState.SEARCH_PERSON, initial_mode="PLAY")
    core.context_snapshot = core.context_snapshot.with_updates(
        k_nav=5,
        pick_retries=2,
        throw_confirmed=True,
        object_detected=True,
        person_detected=True,
        manual_override_active=True,
    )

    status = core.step("vc_abort")

    assert core.current_state == TransitionState.IDLE
    assert core.context_snapshot.mode is None
    assert core.context_snapshot.k_nav == 0
    assert core.context_snapshot.pick_retries == 0
    assert core.context_snapshot.throw_confirmed is False
    assert core.context_snapshot.object_detected is False
    assert core.context_snapshot.person_detected is False
    assert core.context_snapshot.manual_override_active is False
    assert status["last_dispatched_actions_count"] == 2
    assert len(core.skills.nav2.history) == 1
    assert core.skills.nav2.history[0]["request"] == "cancel"
    assert len(core.skills.manip.history) == 1
    assert core.skills.manip.history[0]["request"] == "pick_cancel"


def test_core_vc_abort_from_interrupted_goes_to_idle_without_resume_magic() -> None:
    core = OrchestratorCore(initial_state=TransitionState.INTERRUPTED, initial_mode="SEARCH")
    core.context_snapshot = core.context_snapshot.with_updates(manual_override_active=True)

    status = core.step("vc_abort")

    assert status["result"] == "transition_applied"
    assert core.current_state == TransitionState.IDLE
    assert core.context_snapshot.manual_override_active is False


def test_core_status_contains_required_diagnostics_fields() -> None:
    core = OrchestratorCore(initial_state=TransitionState.SEARCH_OBJECT_GLOBAL)
    status = core.step("object_detected")

    assert status["backend"] == "stub"
    assert status["active_backend"] == "stub"
    assert "chosen_transition_summary" in status
    assert "timeout_key" in status
    assert "unknown_guard_count" in status
    assert "unknown_guards" in status
    assert "last_dispatched_actions_count" in status
    assert "last_unhandled_tokens_count" in status


class _HookableNav2Skill:
    def __init__(self) -> None:
        self.history: list[dict[str, object]] = []
        self._event_hook = None

    def set_event_hook(self, hook: object) -> None:
        self._event_hook = hook

    def request_navigate(self, goal_type: str, goal_payload: dict[str, object]) -> None:
        self.history.append(
            {
                "request": "navigate",
                "goal_type": goal_type,
                "goal_payload": dict(goal_payload),
            }
        )
        if callable(self._event_hook):
            self._event_hook(TransitionEvent.INTERCEPT_REACHED)

    def request_cancel(self, reason: str) -> None:
        self.history.append({"request": "cancel", "reason": reason})


def test_core_processes_hook_injected_event_without_recursive_step() -> None:
    nav2 = _HookableNav2Skill()
    skills = SkillBundle(
        nav2=nav2,
        manip=ManipulationSkillStub(),
        backend="real_nav2",
    )
    core = OrchestratorCore(
        initial_state=TransitionState.SEARCH_OBJECT_GLOBAL,
        initial_mode="SEARCH",
        skills=skills,
    )

    status = core.step("object_detected")

    assert core.current_state == TransitionState.PICK
    assert status["state"] == TransitionState.PICK.value
    assert status["last_event"] == TransitionEvent.INTERCEPT_REACHED.value
    assert status["chosen_transition_summary"] == "INTERCEPT --intercept_reached--> PICK"
    assert len(nav2.history) == 1
