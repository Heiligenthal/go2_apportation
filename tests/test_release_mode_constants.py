from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

NAV2_AVAILABLE = importlib.util.find_spec("nav2_msgs") is not None

pytestmark = [
    pytest.mark.nav2,
    pytest.mark.skipif(
        not NAV2_AVAILABLE,
        reason="nav2_msgs not available in this environment (baseline ros-base)",
    ),
]

if NAV2_AVAILABLE:
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.release_mode_constants import (
        RELEASE_MODE_DROP_SAFE,
        RELEASE_MODE_HANDOVER_RELEASE,
        RELEASE_MODE_OPEN_GRIPPER,
        resolve_release_mode_value,
    )


def test_release_mode_values_baseline() -> None:
    assert RELEASE_MODE_OPEN_GRIPPER == 0
    assert RELEASE_MODE_DROP_SAFE == 1
    assert RELEASE_MODE_HANDOVER_RELEASE == 2


def test_default_release_mode_uses_open_gripper_constant() -> None:
    assert resolve_release_mode_value(None) == RELEASE_MODE_OPEN_GRIPPER
    assert resolve_release_mode_value("") == RELEASE_MODE_OPEN_GRIPPER
    assert resolve_release_mode_value("unknown") == RELEASE_MODE_OPEN_GRIPPER


def test_named_release_modes_map_to_constants() -> None:
    assert resolve_release_mode_value("OPEN_GRIPPER") == RELEASE_MODE_OPEN_GRIPPER
    assert resolve_release_mode_value("DROP_SAFE") == RELEASE_MODE_DROP_SAFE
    assert resolve_release_mode_value("HANDOVER_RELEASE") == RELEASE_MODE_HANDOVER_RELEASE


def test_ros_client_uses_mapping_not_magic_zero() -> None:
    client_file = Path(
        "src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_ros_client.py"
    )
    content = client_file.read_text(encoding="utf-8")

    assert "resolve_release_mode_value(mode)" in content
    assert "request.release_mode = 0" not in content
