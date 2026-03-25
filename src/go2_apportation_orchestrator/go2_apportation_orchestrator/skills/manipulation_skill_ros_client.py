from __future__ import annotations

from dataclasses import dataclass, field

from go2_apportation_msgs.action import PickObject
from go2_apportation_msgs.srv import ReleaseObject
from rclpy.action import ActionClient
from rclpy.node import Node

from .release_mode_constants import (
    RELEASE_MODE_OPEN_GRIPPER,
    resolve_release_mode_value,
)


@dataclass
class ManipulationSkillRosClient:
    node: Node
    pick_action_name: str = "/manipulation/pick"
    release_service_name: str = "/manipulation/release"
    history: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._pick_client = ActionClient(self.node, PickObject, self.pick_action_name)
        self._release_client = self.node.create_client(ReleaseObject, self.release_service_name)
        self._active_pick_goal_handle = None
        self._pending_pick_cancel_reason: str | None = None
        self._pending_pick_goal_futures: list[object] = []

    def request_pick(self, target: dict[str, object]) -> None:
        goal_msg = PickObject.Goal()

        if not self._pick_client.server_is_ready():
            self.history.append(
                {
                    "request": "pick",
                    "target": dict(target),
                    "status": "server_not_ready",
                }
            )
            return

        future = self._pick_client.send_goal_async(goal_msg)
        self._pending_pick_goal_futures.append(future)
        future.add_done_callback(self._on_pick_goal_response)
        self.history.append(
            {
                "request": "pick",
                "target": dict(target),
                "status": "goal_sent",
            }
        )

    def request_release(self, mode: str | int | None, verify_open: bool = True) -> None:
        request = ReleaseObject.Request()
        # Default if no/unknown mode is provided: OPEN_GRIPPER.
        if isinstance(mode, int):
            request.release_mode = mode
        else:
            request.release_mode = resolve_release_mode_value(mode)
        request.verify_open = bool(verify_open)

        if not self._release_client.service_is_ready():
            self.history.append(
                {
                    "request": "release",
                    "mode": mode,
                    "verify_open": request.verify_open,
                    "status": "service_not_ready",
                }
            )
            return

        self._release_client.call_async(request)
        self.history.append(
            {
                "request": "release",
                "mode": mode,
                "verify_open": request.verify_open,
                "release_mode_value": request.release_mode,
                "default_open_gripper": request.release_mode == RELEASE_MODE_OPEN_GRIPPER,
                "status": "request_sent",
            }
        )

    def request_pick_cancel(self, reason: str) -> None:
        if self._active_pick_goal_handle is None:
            self._pending_pick_cancel_reason = reason
            self.history.append(
                {
                    "request": "pick_cancel",
                    "reason": reason,
                    "status": "pending_until_goal_accept",
                }
            )
            return

        self._active_pick_goal_handle.cancel_goal_async()
        self.history.append(
            {
                "request": "pick_cancel",
                "reason": reason,
                "status": "cancel_requested",
            }
        )

    def _on_pick_goal_response(self, future: object) -> None:
        if future in self._pending_pick_goal_futures:
            self._pending_pick_goal_futures.remove(future)
        try:
            goal_handle = future.result()
        except Exception as exc:  # pragma: no cover - defensive ROS callback path
            self.history.append(
                {
                    "request": "pick",
                    "status": "goal_send_error",
                    "error": str(exc),
                }
            )
            return

        self._active_pick_goal_handle = goal_handle
        self.history.append(
            {
                "request": "pick",
                "status": "accepted" if goal_handle.accepted else "rejected",
            }
        )

        if not goal_handle.accepted:
            self._pending_pick_cancel_reason = None
            return

        if self._pending_pick_cancel_reason is not None:
            reason = self._pending_pick_cancel_reason
            self._pending_pick_cancel_reason = None
            goal_handle.cancel_goal_async()
            self.history.append(
                {
                    "request": "pick_cancel",
                    "reason": reason,
                    "status": "cancel_requested_after_accept",
                }
            )
