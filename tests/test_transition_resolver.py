from __future__ import annotations

from dataclasses import replace

import pytest

from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_resolver import (
    resolve_transition_candidates,
    select_first_unguarded,
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
def test_manual_override_active_prioritized_to_interrupted(state: TransitionState) -> None:
    candidates = resolve_transition_candidates(state, TransitionEvent.MANUAL_OVERRIDE_ACTIVE)

    assert candidates
    assert candidates[0].row.to_state == TransitionState.INTERRUPTED
    assert candidates[0].row.event == TransitionEvent.MANUAL_OVERRIDE_ACTIVE
    assert candidates[0].row.from_state == TransitionState.ANY


def test_manual_override_released_has_no_auto_resume_behavior() -> None:
    candidates = resolve_transition_candidates(
        TransitionState.INTERRUPTED,
        TransitionEvent.MANUAL_OVERRIDE_RELEASED,
    )

    assert candidates
    assert all(c.row.to_state == TransitionState.INTERRUPTED for c in candidates)
    assert all(c.row.event == TransitionEvent.MANUAL_OVERRIDE_RELEASED for c in candidates)
    # Resolver does not infer previous state / auto-resume target.
    assert all(c.row.to_state != TransitionState.IDLE for c in candidates)


def test_deterministic_candidate_order_for_same_input() -> None:
    first = resolve_transition_candidates(
        TransitionState.INTERCEPT, TransitionEvent.INTERCEPT_REACHED
    )
    second = resolve_transition_candidates(
        TransitionState.INTERCEPT, TransitionEvent.INTERCEPT_REACHED
    )

    first_signature = [
        (c.row.from_state.value, c.row.event.value, c.row.guard_expr, c.row.to_state.value)
        for c in first
    ]
    second_signature = [
        (c.row.from_state.value, c.row.event.value, c.row.guard_expr, c.row.to_state.value)
        for c in second
    ]

    assert first_signature == second_signature
    assert len(first_signature) == 2


def test_first_unguarded_helper() -> None:
    guarded_only = resolve_transition_candidates(
        TransitionState.INTERCEPT, TransitionEvent.INTERCEPT_REACHED
    )
    assert select_first_unguarded(guarded_only) is None

    with_unguarded = resolve_transition_candidates(
        TransitionState.OBSERVE_HAND, TransitionEvent.MANUAL_OVERRIDE_ACTIVE
    )
    first_unguarded = select_first_unguarded(with_unguarded)
    assert first_unguarded is not None
    assert first_unguarded.row.to_state == TransitionState.INTERRUPTED


def test_duplicate_rows_are_deduplicated_by_signature() -> None:
    base_row = next(
        row
        for row in TRANSITIONS_BASELINE
        if row.from_state == TransitionState.ANY
        and row.event == TransitionEvent.MANUAL_OVERRIDE_ACTIVE
    )
    duplicate_with_other_metadata = replace(
        base_row,
        source_table="duplicate_source_table",
        notes="same transition semantics",
    )

    candidates = resolve_transition_candidates(
        TransitionState.OBSERVE_HAND,
        TransitionEvent.MANUAL_OVERRIDE_ACTIVE,
        transitions=(base_row, duplicate_with_other_metadata, base_row),
    )

    assert len(candidates) == 1
    assert candidates[0].row.to_state == TransitionState.INTERRUPTED
