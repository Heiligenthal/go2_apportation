from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .transition_spec import (
    NO_GUARD_TOKEN,
    PriorityGroup,
    TransitionEvent,
    TransitionRow,
    TransitionState,
    TRANSITIONS_BASELINE,
)


@dataclass(frozen=True)
class TransitionCandidate:
    row: TransitionRow
    guarded: bool
    group_rank: int
    priority_order: int
    baseline_index: int


_PRIORITY_GROUP_ORDER: dict[PriorityGroup, int] = {
    PriorityGroup.ANY_STATE_INTERRUPT: 0,
    PriorityGroup.ANY_STATE_SAFETY: 1,
    PriorityGroup.ANY_STATE_OPERATOR: 2,
    PriorityGroup.MODE_AND_PERSON: 3,
    PriorityGroup.PLAY_FLOW: 4,
    PriorityGroup.SEARCH_FLOW: 5,
    PriorityGroup.INTERCEPT_PICK_RETURN_FOLLOW_RELEASE: 6,
}


def _is_guarded(guard_tokens: tuple[str, ...]) -> bool:
    if not guard_tokens:
        return False
    return not all(token in ("", NO_GUARD_TOKEN) for token in guard_tokens)


def _row_priority_order(row: TransitionRow) -> int:
    # Optional extension point: if TransitionRow later gets priority_order, resolver honors it.
    return int(getattr(row, "priority_order", 0))


def _dedup_key(row: TransitionRow) -> tuple[object, ...]:
    return (
        row.from_state,
        row.event,
        tuple(row.guard_tokens),
        tuple(row.action_tokens),
        row.to_state,
        row.timeout_key,
    )


def resolve_transition_candidates(
    current_state: TransitionState,
    event: TransitionEvent,
    transitions: Iterable[TransitionRow] = TRANSITIONS_BASELINE,
) -> list[TransitionCandidate]:
    candidates: list[TransitionCandidate] = []
    seen_transition_keys: set[tuple[object, ...]] = set()

    for index, row in enumerate(transitions):
        from_matches = row.from_state in (current_state, TransitionState.ANY)
        if row.event != event or not from_matches:
            continue

        dedup_key = _dedup_key(row)
        if dedup_key in seen_transition_keys:
            continue
        seen_transition_keys.add(dedup_key)

        group_rank = _PRIORITY_GROUP_ORDER.get(row.priority_group, 999)
        candidates.append(
            TransitionCandidate(
                row=row,
                guarded=_is_guarded(row.guard_tokens),
                group_rank=group_rank,
                priority_order=_row_priority_order(row),
                baseline_index=index,
            )
        )

    candidates.sort(key=lambda c: (c.group_rank, c.priority_order, c.baseline_index))
    return candidates


def select_first_unguarded(
    candidates: Iterable[TransitionCandidate],
) -> Optional[TransitionCandidate]:
    for candidate in candidates:
        if not candidate.guarded:
            return candidate
    return None
