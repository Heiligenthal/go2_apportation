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
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.action_token_dispatcher import (
        dispatch_action_tokens,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.real_backend_placeholder import (
        ManipulationSkillRealPlaceholder,
        Nav2SkillRealPlaceholder,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.skill_bundle import (
        SkillBundle,
    )


def test_dispatch_nav_goal_token_records_nav_history() -> None:
    skills = SkillBundle()

    result = dispatch_action_tokens(("nav_goal(intercept_goal)",), skills)

    assert len(result) == 1
    assert result[0]["status"] == "dispatched"
    assert result[0]["kind"] == "nav_goal"
    assert len(skills.nav2.history) == 1
    assert skills.nav2.history[0]["request"] == "navigate"
    assert skills.nav2.history[0]["goal_type"] == "intercept_goal"
    assert result[0]["pose_provided"] is False


def test_dispatch_unhandled_token_reports_unhandled() -> None:
    skills = SkillBundle()

    result = dispatch_action_tokens(("set_mode(PLAY)",), skills)

    assert len(result) == 1
    assert result[0]["status"] == "unhandled"
    assert result[0]["unhandled_reason"] == "unsupported_token"
    assert skills.nav2.history == []
    assert skills.manip.history == []


def test_dispatch_pick_and_release_record_manip_history() -> None:
    skills = SkillBundle()

    result = dispatch_action_tokens(("start_pick(object_pose)", "release()"), skills)

    assert [item["status"] for item in result] == ["dispatched", "dispatched"]
    assert len(skills.manip.history) == 2
    assert skills.manip.history[0]["request"] == "pick"
    assert skills.manip.history[0]["target"]["expr"] == "object_pose"
    assert skills.manip.history[1]["request"] == "release"
    assert skills.manip.history[1]["mode"] == "OPEN_GRIPPER"


def test_dispatch_pick_cancel_token_records_cancel() -> None:
    skills = SkillBundle()

    result = dispatch_action_tokens(("pick_cancel()",), skills)

    assert len(result) == 1
    assert result[0]["status"] == "dispatched"
    assert result[0]["kind"] == "pick_cancel"
    assert len(skills.manip.history) == 1
    assert skills.manip.history[0]["request"] == "pick_cancel"


def test_dispatch_real_backend_reports_backend_unavailable() -> None:
    skills = SkillBundle(
        nav2=Nav2SkillRealPlaceholder(),
        manip=ManipulationSkillRealPlaceholder(),
        backend="real_placeholder",
    )

    result = dispatch_action_tokens(("nav_goal(intercept_goal)",), skills)

    assert len(result) == 1
    assert result[0]["status"] == "unhandled"
    assert result[0]["unhandled_reason"] == "backend_unavailable"


def test_dispatch_nav_goal_demo_pose_injection_disabled_by_default() -> None:
    skills = SkillBundle()

    result = dispatch_action_tokens(("nav_goal(intercept_goal)",), skills)

    assert result[0]["status"] == "dispatched"
    assert result[0]["pose_provided"] is False
    assert "x" not in skills.nav2.history[0]["goal_payload"]


def test_dispatch_nav_goal_demo_pose_injection_when_enabled() -> None:
    skills = SkillBundle()

    result = dispatch_action_tokens(
        ("nav_goal(intercept_goal)",),
        skills,
        nav_goal_demo_pose={"frame_id": "map", "x": 0.0, "y": 0.0, "yaw": 0.0},
    )

    assert result[0]["status"] == "dispatched"
    assert result[0]["pose_provided"] is True
    assert result[0]["pose_source"] == "demo_pose_param"
    assert skills.nav2.history[0]["goal_payload"]["frame_id"] == "map"
