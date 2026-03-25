from __future__ import annotations

from typing import Protocol


class Nav2SkillInterface(Protocol):
    history: list[dict[str, object]]

    def request_navigate(self, goal_type: str, goal_payload: dict[str, object]) -> None:
        ...

    def request_cancel(self, reason: str) -> None:
        ...


class ManipulationSkillInterface(Protocol):
    history: list[dict[str, object]]

    def request_pick(self, target: dict[str, object]) -> None:
        ...

    def request_pick_cancel(self, reason: str) -> None:
        ...

    def request_release(self, mode: str | int | None, verify_open: bool = True) -> None:
        ...
