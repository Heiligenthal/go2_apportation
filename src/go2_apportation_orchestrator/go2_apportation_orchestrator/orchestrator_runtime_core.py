from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from .action_token_dispatcher import dispatch_action_tokens
from .skills.skill_bundle import SkillBundle
from .transition_context import ContextSnapshot
from .transition_engine_pure import resolve_first_matching_transition, apply_transition
from .transition_spec import NO_TIMEOUT_KEY, TransitionEvent, TransitionRow, TransitionState


_ALLOWED_WHILE_INTERRUPTED: frozenset[TransitionEvent] = frozenset(
    {
        TransitionEvent.MANUAL_OVERRIDE_ACTIVE,
        TransitionEvent.MANUAL_OVERRIDE_RELEASED,
        TransitionEvent.VC_RESUME,
        TransitionEvent.VC_ABORT,
    }
)


@dataclass(frozen=True)
class CoreStatus:
    backend: str
    active_backend: str
    state: str
    mode: str
    last_event: str
    result: str
    chosen_transition_summary: str
    last_transition_summary: str
    timeout_key: str
    unknown_guard_count: int
    unknown_guards: tuple[str, ...]
    applied_context_updates: tuple[str, ...]
    applied_counter_updates: tuple[str, ...]
    applied_todos: tuple[str, ...]
    last_dispatched_actions_count: int
    last_unhandled_tokens_count: int
    last_unhandled_tokens: tuple[str, ...]
    last_skill_history_sizes: dict[str, int]
    policy_note: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)



def parse_transition_event(value: str) -> Optional[TransitionEvent]:
    text = value.strip()
    if not text:
        return None

    for event in TransitionEvent:
        if text == event.value or text == event.name:
            return event

    lowered = text.lower()
    uppered = text.upper()
    for event in TransitionEvent:
        if lowered == event.value.lower() or uppered == event.name.upper():
            return event

    return None



def parse_transition_state(value: str) -> Optional[TransitionState]:
    text = value.strip()
    if not text:
        return None

    for state in TransitionState:
        if text == state.value or text == state.name:
            return state

    uppered = text.upper()
    for state in TransitionState:
        if uppered == state.name.upper() or uppered == state.value.upper():
            return state

    return None


class OrchestratorCore:
    """Pure runtime core; no ROS dependencies."""

    def __init__(
        self,
        initial_state: TransitionState = TransitionState.IDLE,
        initial_mode: Optional[str] = None,
        skills: Optional[SkillBundle] = None,
        nav_goal_demo_pose: Optional[dict[str, object]] = None,
    ) -> None:
        mode = initial_mode.strip().upper() if initial_mode else None
        self.current_state: TransitionState = initial_state
        self.context_snapshot: ContextSnapshot = ContextSnapshot(mode=mode)
        self.skills = skills if skills is not None else SkillBundle()
        self._nav_goal_demo_pose = dict(nav_goal_demo_pose) if nav_goal_demo_pose else None
        self._in_core_step = False
        self._queued_events: list[TransitionEvent] = []
        self.backend = getattr(self.skills, "backend", "stub")
        self._configure_backend_event_hooks()
        self._last_status = CoreStatus(
            backend=self.backend,
            active_backend=self.backend,
            state=self.current_state.value,
            mode=self.context_snapshot.mode or "",
            last_event="",
            result="initialized",
            chosen_transition_summary="",
            last_transition_summary="",
            timeout_key=NO_TIMEOUT_KEY,
            unknown_guard_count=0,
            unknown_guards=(),
            applied_context_updates=(),
            applied_counter_updates=(),
            applied_todos=(),
            last_dispatched_actions_count=0,
            last_unhandled_tokens_count=0,
            last_unhandled_tokens=(),
            last_skill_history_sizes=self._history_sizes(),
            policy_note="",
        )

    def get_status(self) -> dict[str, object]:
        return self._last_status.to_dict()

    def step(self, event_text: str) -> dict[str, object]:
        event = parse_transition_event(event_text)
        if event is None:
            self._last_status = CoreStatus(
                backend=self.backend,
                active_backend=self.backend,
                state=self.current_state.value,
                mode=self.context_snapshot.mode or "",
                last_event=event_text,
                result="unknown_event",
                chosen_transition_summary="",
                last_transition_summary="",
                timeout_key=NO_TIMEOUT_KEY,
                unknown_guard_count=0,
                unknown_guards=(),
                applied_context_updates=(),
                applied_counter_updates=(),
                applied_todos=(),
                last_dispatched_actions_count=0,
                last_unhandled_tokens_count=0,
                last_unhandled_tokens=(),
                last_skill_history_sizes=self._history_sizes(),
                policy_note="event string not mapped to TransitionEvent",
            )
            return self.get_status()

        return self.step_event(event)

    def step_event(self, event: TransitionEvent) -> dict[str, object]:
        return self.inject_event_enum(event)

    def inject_event_enum(self, event: TransitionEvent) -> dict[str, object]:
        if self._in_core_step:
            self._queued_events.append(event)
            return self.get_status()

        self._in_core_step = True
        try:
            self._step_event_impl(event)
            while self._queued_events:
                queued_event = self._queued_events.pop(0)
                self._step_event_impl(queued_event)
        finally:
            self._in_core_step = False
        return self.get_status()

    def _step_event_impl(self, event: TransitionEvent) -> None:
        if (
            self.current_state == TransitionState.INTERRUPTED
            and event not in _ALLOWED_WHILE_INTERRUPTED
        ):
            self._last_status = CoreStatus(
                backend=self.backend,
                active_backend=self.backend,
                state=self.current_state.value,
                mode=self.context_snapshot.mode or "",
                last_event=event.value,
                result="policy_blocked",
                chosen_transition_summary="",
                last_transition_summary="",
                timeout_key=NO_TIMEOUT_KEY,
                unknown_guard_count=0,
                unknown_guards=(),
                applied_context_updates=(),
                applied_counter_updates=(),
                applied_todos=(),
                last_dispatched_actions_count=0,
                last_unhandled_tokens_count=0,
                last_unhandled_tokens=(),
                last_skill_history_sizes=self._history_sizes(),
                policy_note=(
                    "Policy stub: while INTERRUPTED only manual override events, vc_resume, "
                    "and vc_abort are accepted."
                ),
            )
            return

        transition_row, diagnostics = resolve_first_matching_transition(
            current_state=self.current_state,
            event=event,
            ctx=self.context_snapshot,
        )

        if transition_row is None:
            raw_unknown_tokens = tuple(d.token for d in diagnostics.unknown_guards)
            unknown_tokens = self._truncate_unknown_tokens(raw_unknown_tokens)
            self._last_status = CoreStatus(
                backend=self.backend,
                active_backend=self.backend,
                state=self.current_state.value,
                mode=self.context_snapshot.mode or "",
                last_event=event.value,
                result="no_transition",
                chosen_transition_summary="",
                last_transition_summary="",
                timeout_key=NO_TIMEOUT_KEY,
                unknown_guard_count=len(raw_unknown_tokens),
                unknown_guards=unknown_tokens,
                applied_context_updates=(),
                applied_counter_updates=(),
                applied_todos=(),
                last_dispatched_actions_count=0,
                last_unhandled_tokens_count=0,
                last_unhandled_tokens=(),
                last_skill_history_sizes=self._history_sizes(),
                policy_note="",
            )
            return

        old_state = self.current_state
        new_state, new_ctx, effects = apply_transition(
            current_state=self.current_state,
            transition_row=transition_row,
            ctx=self.context_snapshot,
        )

        self.current_state = new_state
        self.context_snapshot = new_ctx

        dispatch_results = dispatch_action_tokens(
            transition_row.action_tokens,
            self.skills,
            nav_goal_demo_pose=self._nav_goal_demo_pose,
        )
        if event == TransitionEvent.VC_ABORT:
            dispatched_kinds = {
                str(item.get("kind", ""))
                for item in dispatch_results
                if str(item.get("status", "")) == "dispatched"
            }
            dispatch_results.extend(self._dispatch_abort_cancels(dispatched_kinds))

        unhandled_tokens = tuple(
            str(item.get("token", ""))
            for item in dispatch_results
            if str(item.get("status", "")) == "unhandled"
        )

        raw_unknown_tokens = tuple(d.token for d in diagnostics.unknown_guards)
        unknown_tokens = self._truncate_unknown_tokens(raw_unknown_tokens)
        self._last_status = self._build_transition_status(
            old_state=old_state,
            event=event,
            transition_row=transition_row,
            unknown_guard_count=len(raw_unknown_tokens),
            unknown_tokens=unknown_tokens,
            timeout_key=effects.timeout_key,
            context_updates=effects.context_updates,
            counter_updates=effects.counter_updates,
            todos=effects.todos,
            dispatched_actions_count=sum(
                1 for item in dispatch_results if str(item.get("status", "")) == "dispatched"
            ),
            unhandled_tokens=unhandled_tokens,
        )
        return

    def _build_transition_status(
        self,
        old_state: TransitionState,
        event: TransitionEvent,
        transition_row: TransitionRow,
        unknown_guard_count: int,
        unknown_tokens: tuple[str, ...],
        timeout_key: str,
        context_updates: tuple[str, ...],
        counter_updates: tuple[str, ...],
        todos: tuple[str, ...],
        dispatched_actions_count: int,
        unhandled_tokens: tuple[str, ...],
    ) -> CoreStatus:
        summary = f"{old_state.value} --{event.value}--> {transition_row.to_state.value}"
        return CoreStatus(
            backend=self.backend,
            active_backend=self.backend,
            state=self.current_state.value,
            mode=self.context_snapshot.mode or "",
            last_event=event.value,
            result="transition_applied",
            chosen_transition_summary=summary,
            last_transition_summary=summary,
            timeout_key=timeout_key,
            unknown_guard_count=unknown_guard_count,
            unknown_guards=unknown_tokens,
            applied_context_updates=context_updates,
            applied_counter_updates=counter_updates,
            applied_todos=todos,
            last_dispatched_actions_count=dispatched_actions_count,
            last_unhandled_tokens_count=len(unhandled_tokens),
            last_unhandled_tokens=unhandled_tokens,
            last_skill_history_sizes=self._history_sizes(),
            policy_note="",
        )

    def _dispatch_abort_cancels(
        self,
        already_dispatched_kinds: set[str],
    ) -> list[dict[str, object]]:
        effects: list[dict[str, object]] = []

        if "nav_cancel" not in already_dispatched_kinds:
            try:
                self.skills.nav2.request_cancel(reason="vc_abort")
                effects.append(
                    {
                        "token": "abort_effect_nav_cancel",
                        "handled": True,
                        "kind": "nav_cancel",
                        "status": "dispatched",
                        "reason": "vc_abort",
                    }
                )
            except NotImplementedError as exc:
                effects.append(
                    {
                        "token": "abort_effect_nav_cancel",
                        "handled": False,
                        "kind": "nav_cancel",
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )

        if "pick_cancel" not in already_dispatched_kinds:
            try:
                self.skills.manip.request_pick_cancel(reason="vc_abort")
                effects.append(
                    {
                        "token": "abort_effect_pick_cancel",
                        "handled": True,
                        "kind": "pick_cancel",
                        "status": "dispatched",
                        "reason": "vc_abort",
                    }
                )
            except NotImplementedError as exc:
                effects.append(
                    {
                        "token": "abort_effect_pick_cancel",
                        "handled": False,
                        "kind": "pick_cancel",
                        "status": "unhandled",
                        "unhandled_reason": "backend_unavailable",
                        "error": str(exc),
                    }
                )

        return effects

    def _history_sizes(self) -> dict[str, int]:
        return {
            "nav2_history_len": len(getattr(self.skills.nav2, "history", [])),
            "manip_history_len": len(getattr(self.skills.manip, "history", [])),
        }

    def _truncate_unknown_tokens(self, tokens: tuple[str, ...], limit: int = 10) -> tuple[str, ...]:
        if len(tokens) <= limit:
            return tokens
        truncated = list(tokens[:limit])
        truncated.append(f"... ({len(tokens) - limit} more)")
        return tuple(truncated)

    def _configure_backend_event_hooks(self) -> None:
        set_event_hook = getattr(self.skills.nav2, "set_event_hook", None)
        if not callable(set_event_hook):
            return
        set_event_hook(self.inject_event_enum)
