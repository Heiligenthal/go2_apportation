from __future__ import annotations

from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_context import (
    ContextSnapshot,
)
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_engine_pure import (
    apply_transition,
)
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_spec import (
    TRANSITIONS_BASELINE,
    TransitionEvent,
    TransitionState,
)



def _first_row(event: TransitionEvent, from_state: TransitionState) -> object:
    return next(
        row
        for row in TRANSITIONS_BASELINE
        if row.event == event and row.from_state == from_state
    )


def test_vc_lets_play_sets_mode_play() -> None:
    row = _first_row(TransitionEvent.VC_LETS_PLAY, TransitionState.IDLE)

    _, new_ctx, _ = apply_transition(
        current_state=TransitionState.IDLE,
        transition_row=row,
        ctx=ContextSnapshot(mode=None),
    )

    assert new_ctx.mode == "PLAY"


def test_vc_search_sets_mode_search() -> None:
    row = _first_row(TransitionEvent.VC_SEARCH, TransitionState.IDLE)

    _, new_ctx, _ = apply_transition(
        current_state=TransitionState.IDLE,
        transition_row=row,
        ctx=ContextSnapshot(mode=None),
    )

    assert new_ctx.mode == "SEARCH"


def test_manual_override_active_does_not_change_mode() -> None:
    row = _first_row(TransitionEvent.MANUAL_OVERRIDE_ACTIVE, TransitionState.ANY)

    _, new_ctx, _ = apply_transition(
        current_state=TransitionState.OBSERVE_HAND,
        transition_row=row,
        ctx=ContextSnapshot(mode="PLAY", manual_override_active=False),
    )

    assert new_ctx.mode == "PLAY"
    assert new_ctx.manual_override_active is True


def test_vc_abort_resets_mode_and_context_flags() -> None:
    row = _first_row(TransitionEvent.VC_ABORT, TransitionState.ANY)

    _, new_ctx, _ = apply_transition(
        current_state=TransitionState.SEARCH_PERSON,
        transition_row=row,
        ctx=ContextSnapshot(
            mode="SEARCH",
            k_nav=3,
            pick_retries=2,
            throw_confirmed=True,
            object_detected=True,
            person_detected=True,
            manual_override_active=True,
        ),
    )

    assert new_ctx.mode is None
    assert new_ctx.k_nav == 0
    assert new_ctx.pick_retries == 0
    assert new_ctx.throw_confirmed is False
    assert new_ctx.object_detected is False
    assert new_ctx.person_detected is False
    assert new_ctx.manual_override_active is False
