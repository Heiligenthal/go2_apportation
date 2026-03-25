from __future__ import annotations

from dataclasses import dataclass, field

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


@dataclass
class Nav2SkillRosClient:
    node: Node
    action_name: str = "/navigate_to_pose"
    history: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._client = ActionClient(self.node, NavigateToPose, self.action_name)
        self._active_goal_handle = None
        self._pending_cancel_reason: str | None = None
        self._pending_goal_futures: list[object] = []

    def request_navigate(self, goal_type: str, goal_payload: dict[str, object]) -> None:
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()

        if not self._client.server_is_ready():
            self.history.append(
                {
                    "request": "navigate",
                    "goal_type": goal_type,
                    "goal_payload": dict(goal_payload),
                    "status": "server_not_ready",
                }
            )
            return

        future = self._client.send_goal_async(goal_msg)
        self._pending_goal_futures.append(future)
        future.add_done_callback(self._on_goal_response)
        self.history.append(
            {
                "request": "navigate",
                "goal_type": goal_type,
                "goal_payload": dict(goal_payload),
                "status": "goal_sent",
            }
        )

    def request_cancel(self, reason: str) -> None:
        if self._active_goal_handle is None:
            self._pending_cancel_reason = reason
            self.history.append(
                {
                    "request": "cancel",
                    "reason": reason,
                    "status": "pending_until_goal_accept",
                }
            )
            return

        self._active_goal_handle.cancel_goal_async()
        self.history.append(
            {
                "request": "cancel",
                "reason": reason,
                "status": "cancel_requested",
            }
        )

    def _on_goal_response(self, future: object) -> None:
        if future in self._pending_goal_futures:
            self._pending_goal_futures.remove(future)
        try:
            goal_handle = future.result()
        except Exception as exc:  # pragma: no cover - defensive ROS callback path
            self.history.append(
                {
                    "request": "navigate",
                    "status": "goal_send_error",
                    "error": str(exc),
                }
            )
            return

        self._active_goal_handle = goal_handle
        self.history.append(
            {
                "request": "navigate",
                "status": "accepted" if goal_handle.accepted else "rejected",
            }
        )

        if not goal_handle.accepted:
            self._pending_cancel_reason = None
            return

        if self._pending_cancel_reason is not None:
            reason = self._pending_cancel_reason
            self._pending_cancel_reason = None
            goal_handle.cancel_goal_async()
            self.history.append(
                {
                    "request": "cancel",
                    "reason": reason,
                    "status": "cancel_requested_after_accept",
                }
            )
