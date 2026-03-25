from __future__ import annotations

from src.go2_apportation_mocks.go2_apportation_mocks.scenario_config import (
    NAV2_SCENARIOS,
    normalize_scenario,
)


def test_normalize_scenario_accepts_known_value() -> None:
    scenario, used_default = normalize_scenario(
        "hang",
        allowed=NAV2_SCENARIOS,
        default="success",
    )
    assert scenario == "hang"
    assert used_default is False


def test_normalize_scenario_falls_back_for_unknown_value() -> None:
    scenario, used_default = normalize_scenario(
        "invalid",
        allowed=NAV2_SCENARIOS,
        default="success",
    )
    assert scenario == "success"
    assert used_default is True
