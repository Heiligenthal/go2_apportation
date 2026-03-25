from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional


@dataclass(frozen=True)
class ContextSnapshot:
    """Immutable snapshot used by pure transition evaluation/apply functions."""

    mode: Optional[str] = None
    k_nav: int = 0
    pick_retries: int = 0
    throw_confirmed: bool = False
    object_detected: bool = False
    person_detected: bool = False
    manual_override_active: bool = False

    def with_updates(self, **updates: object) -> "ContextSnapshot":
        return replace(self, **updates)
