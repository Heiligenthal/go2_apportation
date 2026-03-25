from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .transition_context import ContextSnapshot
from .transition_resolver import resolve_transition_candidates
from .transition_spec import (
    NO_GUARD_TOKEN,
    TRANSITIONS_BASELINE,
    TransitionEvent,
    TransitionRow,
    TransitionState,
)


@dataclass(frozen=True)
class UnknownGuardDiagnostic:
    token: str
    from_state: TransitionState
    event: TransitionEvent
    to_state: TransitionState
    reason: str = "UNKNOWN_GUARD_TOKEN"


@dataclass(frozen=True)
class ResolveDiagnostics:
    unknown_guards: tuple[UnknownGuardDiagnostic, ...] = ()


@dataclass(frozen=True)
class AppliedTransitionEffects:
    timeout_key: str
    context_updates: tuple[str, ...] = ()
    counter_updates: tuple[str, ...] = ()
    todos: tuple[str, ...] = ()


def _normalize_mode(mode: Optional[str]) -> Optional[str]:
    if mode is None:
        return None
    return mode.strip().upper()


def _split_compound_guard_token(token: str) -> tuple[str, ...]:
    stripped = token.strip()
    if "&" in stripped:
        return tuple(part.strip() for part in stripped.split("&") if part.strip())
    return (stripped,)


def _evaluate_atomic_guard_token(token: str, ctx: ContextSnapshot) -> bool | None:
    stripped = token.strip()
    if stripped in ("", NO_GUARD_TOKEN):
        return True

    normalized = stripped.replace(" ", "")
    lowered = normalized.lower()
    mode = _normalize_mode(ctx.mode)

    if lowered in ("mode=play", "mode==play", "mode==mode.play"):
        return mode == "PLAY"
    if lowered in ("mode=search", "mode==search", "mode==mode.search"):
        return mode == "SEARCH"

    if lowered == "k_nav<2":
        return ctx.k_nav < 2
    if lowered == "k_nav>=2":
        return ctx.k_nav >= 2

    if lowered in ("pick_retries<2", "pickretries<2", "retries<2"):
        return ctx.pick_retries < 2
    if lowered in ("pick_retries>=2", "pickretries>=2", "retries>=2"):
        return ctx.pick_retries >= 2

    if lowered == "throw_confirmed":
        return ctx.throw_confirmed
    if lowered == "object_detected":
        return ctx.object_detected
    if lowered == "person_detected":
        return ctx.person_detected
    if lowered == "manual_override_active":
        return ctx.manual_override_active

    return None


def _collect_unknown_guard_tokens(
    guard_tokens: tuple[str, ...],
    ctx: ContextSnapshot,
) -> tuple[str, ...]:
    unknown: list[str] = []

    for token in guard_tokens:
        for atom in _split_compound_guard_token(token):
            if _evaluate_atomic_guard_token(atom, ctx) is None:
                unknown.append(atom)

    return tuple(unknown)


def evaluate_guard_tokens(
    guard_tokens: tuple[str, ...],
    ctx: ContextSnapshot,
) -> bool | None:
    if not guard_tokens:
        return True

    for token in guard_tokens:
        atoms = _split_compound_guard_token(token)
        if not atoms:
            continue

        for atom in atoms:
            result = _evaluate_atomic_guard_token(atom, ctx)
            if result is None:
                return None
            if not result:
                return False

    return True


def resolve_first_matching_transition(
    current_state: TransitionState,
    event: TransitionEvent,
    ctx: ContextSnapshot,
    transitions: Iterable[TransitionRow] = TRANSITIONS_BASELINE,
) -> tuple[Optional[TransitionRow], ResolveDiagnostics]:
    candidates = resolve_transition_candidates(
        current_state=current_state,
        event=event,
        transitions=transitions,
    )

    unknown_diagnostics: list[UnknownGuardDiagnostic] = []

    for candidate in candidates:
        if not candidate.guarded:
            return candidate.row, ResolveDiagnostics(unknown_guards=tuple(unknown_diagnostics))

        guard_result = evaluate_guard_tokens(candidate.row.guard_tokens, ctx)
        if guard_result is True:
            return candidate.row, ResolveDiagnostics(unknown_guards=tuple(unknown_diagnostics))

        if guard_result is None:
            for token in _collect_unknown_guard_tokens(candidate.row.guard_tokens, ctx):
                unknown_diagnostics.append(
                    UnknownGuardDiagnostic(
                        token=token,
                        from_state=candidate.row.from_state,
                        event=candidate.row.event,
                        to_state=candidate.row.to_state,
                    )
                )

    return None, ResolveDiagnostics(unknown_guards=tuple(unknown_diagnostics))


def _contains_token_prefix(action_tokens: tuple[str, ...], prefix: str) -> bool:
    prefix_lower = prefix.lower()
    return any(token.strip().lower().startswith(prefix_lower) for token in action_tokens)


def _contains_retry_like_token(action_tokens: tuple[str, ...]) -> bool:
    return any("retry" in token.strip().lower() for token in action_tokens)


def apply_transition(
    current_state: TransitionState,
    transition_row: TransitionRow,
    ctx: ContextSnapshot,
) -> tuple[TransitionState, ContextSnapshot, AppliedTransitionEffects]:
    new_state = transition_row.to_state
    new_ctx = ctx

    context_updates: list[str] = []
    counter_updates: list[str] = []
    todos: list[str] = []

    has_retry_nav = _contains_token_prefix(transition_row.action_tokens, "retry_nav")
    has_retry_pick = _contains_token_prefix(transition_row.action_tokens, "retry_pick")

    if has_retry_nav:
        new_ctx = new_ctx.with_updates(k_nav=new_ctx.k_nav + 1)
        counter_updates.append("k_nav += 1")

    if has_retry_pick:
        new_ctx = new_ctx.with_updates(pick_retries=new_ctx.pick_retries + 1)
        counter_updates.append("pick_retries += 1")

    if _contains_retry_like_token(transition_row.action_tokens) and not (
        has_retry_nav or has_retry_pick
    ):
        todos.append("retry-token present but not recognized; no counter update applied")

    if current_state != TransitionState.INTERRUPTED and new_state == TransitionState.INTERRUPTED:
        new_ctx = new_ctx.with_updates(manual_override_active=True)
        context_updates.append("manual_override_active := True")

    if transition_row.event == TransitionEvent.MANUAL_OVERRIDE_RELEASED:
        new_ctx = new_ctx.with_updates(manual_override_active=False)
        context_updates.append("manual_override_active := False")

    if transition_row.event == TransitionEvent.VC_LETS_PLAY:
        new_ctx = new_ctx.with_updates(mode="PLAY")
        context_updates.append("mode := PLAY")

    if transition_row.event == TransitionEvent.VC_SEARCH:
        new_ctx = new_ctx.with_updates(mode="SEARCH")
        context_updates.append("mode := SEARCH")

    if transition_row.event == TransitionEvent.VC_ABORT:
        new_ctx = new_ctx.with_updates(
            mode=None,
            k_nav=0,
            pick_retries=0,
            throw_confirmed=False,
            object_detected=False,
            person_detected=False,
            manual_override_active=False,
        )
        context_updates.extend(
            (
                "mode := None",
                "k_nav := 0",
                "pick_retries := 0",
                "throw_confirmed := False",
                "object_detected := False",
                "person_detected := False",
                "manual_override_active := False",
            )
        )

    effects = AppliedTransitionEffects(
        timeout_key=transition_row.timeout_key,
        context_updates=tuple(context_updates),
        counter_updates=tuple(counter_updates),
        todos=tuple(todos),
    )

    return new_state, new_ctx, effects
