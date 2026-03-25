from __future__ import annotations

from dataclasses import replace

import pytest

from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_context import (
    ContextSnapshot,
)
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_engine_pure import (
    apply_transition,
    resolve_first_matching_transition,
)
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_spec import (
    TRANSITIONS_BASELINE,
    TransitionEvent,
    TransitionState,
)


@pytest.mark.parametrize(
    "state",
    [
        TransitionState.IDLE,
        TransitionState.OBSERVE_HAND,
        TransitionState.PICK,
    ],
)
def test_manual_override_active_resolves_to_interrupted(state: TransitionState) -> None:
    transition, diagnostics = resolve_first_matching_transition(
        current_state=state,
        event=TransitionEvent.MANUAL_OVERRIDE_ACTIVE,
        ctx=ContextSnapshot(),
    )

    assert transition is not None
    assert transition.to_state == TransitionState.INTERRUPTED
    assert diagnostics.unknown_guards == ()


def test_manual_override_released_has_no_resume_magic() -> None:
    release_transition, _ = resolve_first_matching_transition(
        current_state=TransitionState.INTERRUPTED,
        event=TransitionEvent.MANUAL_OVERRIDE_RELEASED,
        ctx=ContextSnapshot(manual_override_active=True),
    )
    assert release_transition is None or release_transition.to_state == TransitionState.INTERRUPTED

    no_history_transition, _ = resolve_first_matching_transition(
        current_state=TransitionState.IDLE,
        event=TransitionEvent.MANUAL_OVERRIDE_RELEASED,
        ctx=ContextSnapshot(manual_override_active=True),
    )
    assert no_history_transition is None


def test_guard_whitelist_mode_and_boolean_matching() -> None:
    play_ctx = ContextSnapshot(mode="PLAY", throw_confirmed=True)
    play_transition, _ = resolve_first_matching_transition(
        current_state=TransitionState.INTERCEPT,
        event=TransitionEvent.INTERCEPT_REACHED,
        ctx=play_ctx,
    )
    assert play_transition is not None
    assert "MODE=PLAY" in play_transition.guard_tokens
    assert "throw_confirmed" in play_transition.guard_tokens

    play_without_throw = ContextSnapshot(mode="PLAY", throw_confirmed=False)
    no_transition, _ = resolve_first_matching_transition(
        current_state=TransitionState.INTERCEPT,
        event=TransitionEvent.INTERCEPT_REACHED,
        ctx=play_without_throw,
    )
    assert no_transition is None

    search_ctx = ContextSnapshot(mode="SEARCH")
    search_transition, _ = resolve_first_matching_transition(
        current_state=TransitionState.INTERCEPT,
        event=TransitionEvent.INTERCEPT_REACHED,
        ctx=search_ctx,
    )
    assert search_transition is not None
    assert search_transition.guard_tokens == ("MODE=SEARCH",)


def test_unknown_guard_token_is_reported_and_not_matched() -> None:
    template = next(
        row
        for row in TRANSITIONS_BASELINE
        if row.from_state == TransitionState.INTERCEPT
        and row.event == TransitionEvent.INTERCEPT_REACHED
    )
    unknown_guard_transition = replace(
        template,
        guard_expr="mystery_guard",
        guard_tokens=("mystery_guard",),
        to_state=TransitionState.FAILSAFE_ABORT,
    )

    transition, diagnostics = resolve_first_matching_transition(
        current_state=TransitionState.INTERCEPT,
        event=TransitionEvent.INTERCEPT_REACHED,
        ctx=ContextSnapshot(mode="PLAY", throw_confirmed=True),
        transitions=(unknown_guard_transition,),
    )

    assert transition is None
    assert diagnostics.unknown_guards
    assert diagnostics.unknown_guards[0].token == "mystery_guard"


def test_apply_transition_updates_retry_counters() -> None:
    retry_nav_transition = next(
        row
        for row in TRANSITIONS_BASELINE
        if row.from_state == TransitionState.APPROACH_PERSON
        and row.event == TransitionEvent.NAV_FAILED
    )
    retry_pick_transition = next(
        row
        for row in TRANSITIONS_BASELINE
        if row.from_state == TransitionState.PICK
        and row.event == TransitionEvent.GRASP_FAILED
        and "retry_pick(r++)" in row.action_tokens
    )

    _, ctx_after_nav, nav_effects = apply_transition(
        current_state=TransitionState.APPROACH_PERSON,
        transition_row=retry_nav_transition,
        ctx=ContextSnapshot(k_nav=1),
    )
    assert ctx_after_nav.k_nav == 2
    assert "k_nav += 1" in nav_effects.counter_updates

    _, ctx_after_pick, pick_effects = apply_transition(
        current_state=TransitionState.PICK,
        transition_row=retry_pick_transition,
        ctx=ContextSnapshot(pick_retries=0),
    )
    assert ctx_after_pick.pick_retries == 1
    assert "pick_retries += 1" in pick_effects.counter_updates


def test_apply_transition_manual_override_flags() -> None:
    activate = next(
        row
        for row in TRANSITIONS_BASELINE
        if row.event == TransitionEvent.MANUAL_OVERRIDE_ACTIVE
    )
    release = next(
        row
        for row in TRANSITIONS_BASELINE
        if row.event == TransitionEvent.MANUAL_OVERRIDE_RELEASED
    )

    _, after_activate, activate_effects = apply_transition(
        current_state=TransitionState.IDLE,
        transition_row=activate,
        ctx=ContextSnapshot(manual_override_active=False),
    )
    assert after_activate.manual_override_active is True
    assert "manual_override_active := True" in activate_effects.context_updates

    _, after_release, release_effects = apply_transition(
        current_state=TransitionState.INTERRUPTED,
        transition_row=release,
        ctx=ContextSnapshot(manual_override_active=True),
    )
    assert after_release.manual_override_active is False
    assert "manual_override_active := False" in release_effects.context_updates
