from __future__ import annotations

import importlib.util

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
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.manipulation_skill_ros_client import (
        ManipulationSkillRosClient,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.manipulation_skill_stub import (
        ManipulationSkillStub,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.nav2_skill_ros_client import (
        Nav2SkillRosClient,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.nav2_skill_real_client import (
        Nav2SkillRealClient,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.nav2_skill_stub import (
        Nav2SkillStub,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.skill_bundle import (
        create_skill_bundle,
    )


def test_create_skill_bundle_stub_backend() -> None:
    bundle = create_skill_bundle("stub")

    assert bundle.backend == "stub"
    assert bundle.nav2.history == []
    assert bundle.manip.history == []


def test_create_skill_bundle_ros_requires_node() -> None:
    with pytest.raises(ValueError):
        create_skill_bundle("ros")


def test_create_skill_bundle_mock_requires_node() -> None:
    with pytest.raises(ValueError):
        create_skill_bundle("mock")


def test_create_skill_bundle_real_requires_node() -> None:
    with pytest.raises(ValueError):
        create_skill_bundle("real")


def test_create_skill_bundle_real_nav2_requires_node() -> None:
    with pytest.raises(ValueError):
        create_skill_bundle("real_nav2")


def test_create_skill_bundle_unknown_backend_raises() -> None:
    with pytest.raises(ValueError):
        create_skill_bundle("invalid")


def test_skill_classes_expose_consistent_method_names() -> None:
    assert hasattr(Nav2SkillStub, "request_navigate")
    assert hasattr(Nav2SkillStub, "request_cancel")
    assert hasattr(Nav2SkillRosClient, "request_navigate")
    assert hasattr(Nav2SkillRosClient, "request_cancel")
    assert hasattr(Nav2SkillRealClient, "request_navigate")
    assert hasattr(Nav2SkillRealClient, "request_cancel")
    assert hasattr(ManipulationSkillStub, "request_pick")
    assert hasattr(ManipulationSkillStub, "request_pick_cancel")
    assert hasattr(ManipulationSkillStub, "request_release")
    assert hasattr(ManipulationSkillRosClient, "request_pick")
    assert hasattr(ManipulationSkillRosClient, "request_pick_cancel")
    assert hasattr(ManipulationSkillRosClient, "request_release")
