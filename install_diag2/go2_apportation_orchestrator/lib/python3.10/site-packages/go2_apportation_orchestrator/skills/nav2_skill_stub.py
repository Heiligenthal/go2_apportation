from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Nav2SkillStub:
    history: list[dict[str, object]] = field(default_factory=list)

    def request_navigate(self, goal_type: str, goal_payload: dict[str, object]) -> None:
        self.history.append(
            {
                "request": "navigate",
                "goal_type": goal_type,
                "goal_payload": dict(goal_payload),
            }
        )

    def request_cancel(self, reason: str) -> None:
        self.history.append(
            {
                "request": "cancel",
                "reason": reason,
            }
        )
