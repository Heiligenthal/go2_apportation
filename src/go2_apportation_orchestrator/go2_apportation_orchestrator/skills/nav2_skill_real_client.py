from __future__ import annotations

from dataclasses import dataclass, field
import math
import time
from typing import Callable, Optional

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node

from ..transition_spec import TransitionEvent


def infer_nav_success_event(goal_type: str) -> TransitionEvent:
    normalized = goal_type.strip().lower()
    if "intercept" in normalized or "object" in normalized:
        return TransitionEvent.INTERCEPT_REACHED
    return TransitionEvent.APPROACH_REACHED


def map_nav2_result_status_to_event(
    status: int,
    goal_type: str,
) -> TransitionEvent | None:
    if status == GoalStatus.STATUS_SUCCEEDED:
        return infer_nav_success_event(goal_type)
    if status in (GoalStatus.STATUS_ABORTED, GoalStatus.STATUS_CANCELED):
        return TransitionEvent.NAV_FAILED
    return None


@dataclass
class Nav2SkillRealClient:
    node: Node
    action_name: str = "/navigate_to_pose"
    enable_real_motion: bool = False
    server_wait_timeout_s: float = 1.0
    history: list[dict[str, object]] = field(default_factory=list)
    action_client_factory: Optional[Callable[[Node, type, str], object]] = None
    event_hook: Optional[Callable[[TransitionEvent], None]] = None

    def __post_init__(self) -> None:
        factory = self.action_client_factory or self._default_action_client_factory
        self._client = factory(self.node, NavigateToPose, self.action_name)
        self._active_goal_handle = None
        self._pending_cancel_reason: Optional[str] = None
        self._pending_goal_context_by_future: dict[object, dict[str, object]] = {}
        self._pending_result_context_by_future: dict[object, dict[str, object]] = {}

    def request_navigate(self, goal_type: str, goal_payload: dict[str, object]) -> None:
        base_entry = {
            "request": "navigate",
            "backend": "real_nav2",
            "action_name": self.action_name,
            "goal_type": goal_type,
            "goal_payload": dict(goal_payload),
            "timestamp": time.time(),
        }

        if not self.enable_real_motion:
            self._append_history(
                {
                    **base_entry,
                    "status": "motion_disabled",
                    "unhandled_reason": "real_motion_disabled",
                }
            )
            self._log("warn", "real_nav2 motion disabled; skipping goal send")
            return

        pose_msg = self._build_pose_stamped(goal_payload)
        if pose_msg is None:
            self._append_history(
                {
                    **base_entry,
                    "status": "missing_pose",
                    "unhandled_reason": "missing_goal_pose",
                }
            )
            self._log("warn", "real_nav2 missing goal pose; skipping goal send")
            return

        if not self._wait_for_server():
            self._append_history(
                {
                    **base_entry,
                    "status": "server_unavailable",
                    "unhandled_reason": "action_server_unavailable",
                }
            )
            self._log(
                "warn",
                "real_nav2 action server unavailable on %s" % self.action_name,
            )
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose_msg
        future = self._client.send_goal_async(goal_msg)
        self._pending_goal_context_by_future[future] = {
            "goal_type": goal_type,
            "goal_payload": dict(goal_payload),
        }
        future.add_done_callback(self._on_goal_response)
        self._append_history(
            {
                **base_entry,
                "status": "goal_sent",
                "frame_id": pose_msg.header.frame_id,
            }
        )

    def request_cancel(self, reason: str) -> None:
        base_entry = {
            "request": "cancel",
            "backend": "real_nav2",
            "action_name": self.action_name,
            "reason": reason,
            "timestamp": time.time(),
        }

        if self._active_goal_handle is None:
            self._pending_cancel_reason = reason
            self._append_history(
                {
                    **base_entry,
                    "status": "cancel_no_active_goal",
                }
            )
            self._log("info", "real_nav2 cancel requested without active goal; pending set")
            return

        self._active_goal_handle.cancel_goal_async()
        self._append_history(
            {
                **base_entry,
                "status": "cancel_requested",
            }
        )

    def set_event_hook(self, hook: Optional[Callable[[TransitionEvent], None]]) -> None:
        self.event_hook = hook

    def _default_action_client_factory(self, node: Node, action_type: type, action_name: str) -> object:
        return ActionClient(node, action_type, action_name)

    def _wait_for_server(self) -> bool:
        wait_for_server = getattr(self._client, "wait_for_server", None)
        if not callable(wait_for_server):
            return False
        return bool(wait_for_server(timeout_sec=self.server_wait_timeout_s))

    def _on_goal_response(self, future: object) -> None:
        context = self._pending_goal_context_by_future.pop(
            future,
            {
                "goal_type": "",
                "goal_payload": {},
            },
        )

        try:
            goal_handle = future.result()
        except Exception as exc:  # pragma: no cover - defensive ROS callback path
            self._append_history(
                {
                    "request": "navigate",
                    "backend": "real_nav2",
                    "action_name": self.action_name,
                    "status": "goal_response_error",
                    "error": str(exc),
                    "timestamp": time.time(),
                }
            )
            return

        accepted = bool(getattr(goal_handle, "accepted", False))
        self._append_history(
            {
                "request": "navigate",
                "backend": "real_nav2",
                "action_name": self.action_name,
                "status": "goal_accepted" if accepted else "goal_rejected",
                "timestamp": time.time(),
            }
        )

        if not accepted:
            self._pending_cancel_reason = None
            return

        self._active_goal_handle = goal_handle
        get_result_async = getattr(goal_handle, "get_result_async", None)
        if callable(get_result_async):
            result_future = get_result_async()
            self._pending_result_context_by_future[result_future] = context
            result_future.add_done_callback(self._on_result)

        if self._pending_cancel_reason is not None:
            reason = self._pending_cancel_reason
            self._pending_cancel_reason = None
            goal_handle.cancel_goal_async()
            self._append_history(
                {
                    "request": "cancel",
                    "backend": "real_nav2",
                    "action_name": self.action_name,
                    "status": "cancel_requested_after_accept",
                    "reason": reason,
                    "timestamp": time.time(),
                }
            )

    def _on_result(self, future: object) -> None:
        context = self._pending_result_context_by_future.pop(
            future,
            {
                "goal_type": "",
                "goal_payload": {},
            },
        )
        goal_type = str(context.get("goal_type", ""))
        try:
            result_msg = future.result()
        except Exception as exc:  # pragma: no cover - defensive ROS callback path
            self._append_history(
                {
                    "request": "navigate",
                    "backend": "real_nav2",
                    "action_name": self.action_name,
                    "status": "result_callback_error",
                    "error": str(exc),
                    "timestamp": time.time(),
                }
            )
            return

        status_code = int(getattr(result_msg, "status", 0))
        mapped_event = map_nav2_result_status_to_event(status_code, goal_type)

        status_label = "result_unknown"
        if status_code == GoalStatus.STATUS_SUCCEEDED:
            status_label = "result_succeeded"
        elif status_code == GoalStatus.STATUS_ABORTED:
            status_label = "result_aborted"
        elif status_code == GoalStatus.STATUS_CANCELED:
            status_label = "result_canceled"

        self._append_history(
            {
                "request": "navigate",
                "backend": "real_nav2",
                "action_name": self.action_name,
                "status": status_label,
                "result_status_code": status_code,
                "mapped_event": mapped_event.value if mapped_event is not None else "",
                "goal_type": goal_type,
                "timestamp": time.time(),
            }
        )

        self._active_goal_handle = None
        if mapped_event is None:
            return

        if self.event_hook is None:
            self._append_history(
                {
                    "request": "navigate",
                    "backend": "real_nav2",
                    "action_name": self.action_name,
                    "status": "event_hook_missing",
                    "mapped_event": mapped_event.value,
                    "timestamp": time.time(),
                }
            )
            return

        try:
            self.event_hook(mapped_event)
            self._append_history(
                {
                    "request": "navigate",
                    "backend": "real_nav2",
                    "action_name": self.action_name,
                    "status": "event_injected",
                    "mapped_event": mapped_event.value,
                    "timestamp": time.time(),
                }
            )
        except Exception as exc:  # pragma: no cover - defensive ROS callback path
            self._append_history(
                {
                    "request": "navigate",
                    "backend": "real_nav2",
                    "action_name": self.action_name,
                    "status": "event_hook_error",
                    "mapped_event": mapped_event.value,
                    "error": str(exc),
                    "timestamp": time.time(),
                }
            )

    def _build_pose_stamped(self, goal_payload: dict[str, object]) -> Optional[PoseStamped]:
        if not isinstance(goal_payload, dict):
            return None

        if "pose_stamped" in goal_payload and isinstance(goal_payload["pose_stamped"], dict):
            return self._pose_from_pose_stamped_dict(goal_payload["pose_stamped"])

        required = ("x", "y", "yaw", "frame_id")
        if not all(key in goal_payload for key in required):
            return None

        try:
            x = float(goal_payload["x"])
            y = float(goal_payload["y"])
            yaw = float(goal_payload["yaw"])
            frame_id = str(goal_payload["frame_id"])
            z = float(goal_payload.get("z", 0.0))
        except (TypeError, ValueError):
            return None

        pose = PoseStamped()
        pose.header.frame_id = frame_id
        self._fill_stamp(pose)
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def _pose_from_pose_stamped_dict(self, data: dict[str, object]) -> Optional[PoseStamped]:
        header = data.get("header", {})
        pose_data = data.get("pose", {})
        if not isinstance(header, dict) or not isinstance(pose_data, dict):
            return None

        frame_id = str(header.get("frame_id", data.get("frame_id", ""))).strip()
        if not frame_id:
            return None

        position = pose_data.get("position", {})
        orientation = pose_data.get("orientation", {})
        if not isinstance(position, dict) or not isinstance(orientation, dict):
            return None

        try:
            px = float(position["x"])
            py = float(position["y"])
            pz = float(position.get("z", 0.0))
            ox = float(orientation["x"])
            oy = float(orientation["y"])
            oz = float(orientation["z"])
            ow = float(orientation["w"])
        except (KeyError, TypeError, ValueError):
            return None

        pose = PoseStamped()
        pose.header.frame_id = frame_id
        self._fill_stamp(pose)
        pose.pose.position.x = px
        pose.pose.position.y = py
        pose.pose.position.z = pz
        pose.pose.orientation.x = ox
        pose.pose.orientation.y = oy
        pose.pose.orientation.z = oz
        pose.pose.orientation.w = ow
        return pose

    def _fill_stamp(self, pose: PoseStamped) -> None:
        get_clock = getattr(self.node, "get_clock", None)
        if callable(get_clock):
            try:
                pose.header.stamp = get_clock().now().to_msg()
            except Exception:
                return

    def _append_history(self, entry: dict[str, object]) -> None:
        self.history.append(entry)

    def _log(self, level: str, message: str) -> None:
        get_logger = getattr(self.node, "get_logger", None)
        if not callable(get_logger):
            return
        logger = get_logger()
        log_fn = getattr(logger, level, None)
        if callable(log_fn):
            log_fn(message)
