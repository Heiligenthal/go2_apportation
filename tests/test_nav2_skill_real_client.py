from __future__ import annotations

import importlib.util

import pytest
from action_msgs.msg import GoalStatus

NAV2_AVAILABLE = importlib.util.find_spec("nav2_msgs") is not None

pytestmark = [
    pytest.mark.nav2,
    pytest.mark.skipif(
        not NAV2_AVAILABLE,
        reason="nav2_msgs not available in this environment (baseline ros-base)",
    ),
]

if NAV2_AVAILABLE:
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.skills.nav2_skill_real_client import (
        Nav2SkillRealClient,
        map_nav2_result_status_to_event,
    )
    from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_spec import (
        TransitionEvent,
    )


class _FakeLogger:
    def info(self, _msg: str) -> None:
        return

    def warn(self, _msg: str) -> None:
        return


class _FakeNode:
    def get_logger(self) -> _FakeLogger:
        return _FakeLogger()


class _FakeGoalHandle:
    def __init__(self, accepted: bool = True, result_status: int = GoalStatus.STATUS_SUCCEEDED) -> None:
        self.accepted = accepted
        self._result_status = result_status
        self.cancel_requests = 0

    def cancel_goal_async(self) -> None:
        self.cancel_requests += 1

    def get_result_async(self) -> "_FakeFuture":
        return _FakeFuture(_FakeResult(status=self._result_status))


class _FakeResult:
    def __init__(self, status: int) -> None:
        self.status = status


class _FakeFuture:
    def __init__(self, result_obj: object) -> None:
        self._result_obj = result_obj

    def add_done_callback(self, callback: object) -> None:
        callback(self)

    def result(self) -> object:
        return self._result_obj


class _FakeActionClient:
    def __init__(
        self,
        ready: bool = True,
        goal_handle: _FakeGoalHandle | None = None,
    ) -> None:
        self.ready = ready
        self.goal_handle = goal_handle if goal_handle is not None else _FakeGoalHandle(accepted=True)
        self.sent_goals: list[object] = []

    def wait_for_server(self, timeout_sec: float) -> bool:  # noqa: ARG002
        return self.ready

    def send_goal_async(self, goal_msg: object) -> _FakeFuture:
        self.sent_goals.append(goal_msg)
        return _FakeFuture(self.goal_handle)


def test_real_client_motion_disabled_does_not_send_goal() -> None:
    fake_client = _FakeActionClient(ready=True)
    client = Nav2SkillRealClient(
        node=_FakeNode(),
        enable_real_motion=False,
        action_client_factory=lambda _node, _action_type, _action_name: fake_client,
    )

    client.request_navigate(
        "intercept_goal",
        {"x": 1.0, "y": 2.0, "yaw": 0.0, "frame_id": "map"},
    )

    assert client.history[-1]["status"] == "motion_disabled"
    assert client.history[-1]["unhandled_reason"] == "real_motion_disabled"
    assert fake_client.sent_goals == []


def test_real_client_missing_pose_is_diagnosed() -> None:
    fake_client = _FakeActionClient(ready=True)
    client = Nav2SkillRealClient(
        node=_FakeNode(),
        enable_real_motion=True,
        action_client_factory=lambda _node, _action_type, _action_name: fake_client,
    )

    client.request_navigate("intercept_goal", {})

    assert client.history[-1]["status"] == "missing_pose"
    assert client.history[-1]["unhandled_reason"] == "missing_goal_pose"
    assert fake_client.sent_goals == []


def test_real_client_cancel_without_active_goal_is_diagnosed() -> None:
    fake_client = _FakeActionClient(ready=True)
    client = Nav2SkillRealClient(
        node=_FakeNode(),
        enable_real_motion=True,
        action_client_factory=lambda _node, _action_type, _action_name: fake_client,
    )

    client.request_cancel("operator_abort")

    assert client.history[-1]["status"] == "cancel_no_active_goal"


def test_map_nav2_result_status_to_event() -> None:
    assert (
        map_nav2_result_status_to_event(GoalStatus.STATUS_SUCCEEDED, "intercept_goal")
        == TransitionEvent.INTERCEPT_REACHED
    )
    assert (
        map_nav2_result_status_to_event(GoalStatus.STATUS_SUCCEEDED, "person+offset")
        == TransitionEvent.APPROACH_REACHED
    )
    assert (
        map_nav2_result_status_to_event(GoalStatus.STATUS_ABORTED, "intercept_goal")
        == TransitionEvent.NAV_FAILED
    )
    assert (
        map_nav2_result_status_to_event(GoalStatus.STATUS_CANCELED, "intercept_goal")
        == TransitionEvent.NAV_FAILED
    )


def test_real_client_injects_event_via_hook_on_result() -> None:
    fake_client = _FakeActionClient(
        ready=True,
        goal_handle=_FakeGoalHandle(
            accepted=True,
            result_status=GoalStatus.STATUS_SUCCEEDED,
        ),
    )
    client = Nav2SkillRealClient(
        node=_FakeNode(),
        enable_real_motion=True,
        action_client_factory=lambda _node, _action_type, _action_name: fake_client,
    )

    injected_events: list[TransitionEvent] = []
    client.set_event_hook(injected_events.append)
    client.request_navigate(
        "intercept_goal",
        {"x": 1.0, "y": 2.0, "yaw": 0.0, "frame_id": "map"},
    )

    assert injected_events == [TransitionEvent.INTERCEPT_REACHED]
    assert any(entry.get("status") == "event_injected" for entry in client.history)
