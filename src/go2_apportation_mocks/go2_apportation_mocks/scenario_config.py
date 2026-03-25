from __future__ import annotations


NAV2_SCENARIOS: frozenset[str] = frozenset({"success", "fail", "hang"})
PICK_SCENARIOS: frozenset[str] = frozenset({"success", "fail", "hang"})
RELEASE_SCENARIOS: frozenset[str] = frozenset({"success", "fail", "hang"})


def normalize_scenario(
    raw: str | None,
    *,
    allowed: frozenset[str],
    default: str,
) -> tuple[str, bool]:
    text = (raw or "").strip().lower()
    if text in allowed:
        return text, False
    return default, True
