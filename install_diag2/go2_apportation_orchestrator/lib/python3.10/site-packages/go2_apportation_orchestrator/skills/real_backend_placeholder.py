from __future__ import annotations

from dataclasses import dataclass, field


_MESSAGE = "skills backend 'real' is not implemented yet; use 'stub' or 'ros/mock'."


@dataclass
class Nav2SkillRealPlaceholder:
    history: list[dict[str, object]] = field(default_factory=list)

    def request_navigate(self, goal_type: str, goal_payload: dict[str, object]) -> None:
        raise NotImplementedError(_MESSAGE)

    def request_cancel(self, reason: str) -> None:
        raise NotImplementedError(_MESSAGE)


@dataclass
class ManipulationSkillRealPlaceholder:
    history: list[dict[str, object]] = field(default_factory=list)

    def request_pick(self, target: dict[str, object]) -> None:
        raise NotImplementedError(_MESSAGE)

    def request_pick_cancel(self, reason: str) -> None:
        raise NotImplementedError(_MESSAGE)

    def request_release(self, mode: str | int | None, verify_open: bool = True) -> None:
        raise NotImplementedError(_MESSAGE)
