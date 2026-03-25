from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ManipulationSkillStub:
    history: list[dict[str, object]] = field(default_factory=list)

    def request_pick(self, target: dict[str, object]) -> None:
        self.history.append(
            {
                "request": "pick",
                "target": dict(target),
            }
        )

    def request_release(self, mode: str | int | None, verify_open: bool = True) -> None:
        self.history.append(
            {
                "request": "release",
                "mode": mode,
                "verify_open": verify_open,
            }
        )

    def request_pick_cancel(self, reason: str) -> None:
        self.history.append(
            {
                "request": "pick_cancel",
                "reason": reason,
            }
        )
