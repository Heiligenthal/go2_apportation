from __future__ import annotations

import json
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .orchestrator_runtime_core import OrchestratorCore, parse_transition_state
from .skills import create_skill_bundle
from .transition_spec import TransitionState


class OrchestratorRuntimeNode(Node):
    """Phase-2.4 runtime skeleton.

    This node performs deterministic state transitions from incoming events using
    the pure transition modules. It intentionally does not execute Nav2/MoveIt
    actions and does not publish cmd_vel.
    """

    def __init__(self) -> None:
        super().__init__("orchestrator_runtime")

        self.declare_parameter("initial_state", "IDLE")
        self.declare_parameter("initial_mode", "")
        self.declare_parameter("debug", True)
        self.declare_parameter("publish_rate_hz", 2.0)
        self.declare_parameter("skills_backend", "stub")
        self.declare_parameter("enable_real_motion", False)
        self.declare_parameter("enable_demo_pose", False)
        self.declare_parameter("nav2_action_name", "/navigate_to_pose")

        initial_state_param = str(self.get_parameter("initial_state").value)
        initial_mode_param = str(self.get_parameter("initial_mode").value)
        self._debug = bool(self.get_parameter("debug").value)
        self._publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        skills_backend = str(self.get_parameter("skills_backend").value)
        self._enable_real_motion = bool(self.get_parameter("enable_real_motion").value)
        self._enable_demo_pose = bool(self.get_parameter("enable_demo_pose").value)
        self._nav2_action_name = str(self.get_parameter("nav2_action_name").value)

        initial_state = parse_transition_state(initial_state_param)
        if initial_state is None:
            self.get_logger().warn(
                "Unknown initial_state '%s'; fallback to IDLE." % initial_state_param
            )
            initial_state = TransitionState.IDLE

        initial_mode = initial_mode_param.strip() or None
        try:
            skills = create_skill_bundle(
                skills_backend,
                node=self,
                enable_real_motion=self._enable_real_motion,
                nav2_action_name=self._nav2_action_name,
            )
        except ValueError:
            self.get_logger().warn(
                "Unknown skills_backend '%s'; fallback to stub." % skills_backend
            )
            skills_backend = "stub"
            skills = create_skill_bundle(
                "stub",
                node=self,
                enable_real_motion=self._enable_real_motion,
                nav2_action_name=self._nav2_action_name,
            )

        self.core = OrchestratorCore(
            initial_state=initial_state,
            initial_mode=initial_mode,
            skills=skills,
            nav_goal_demo_pose=(
                {"frame_id": "map", "x": 0.0, "y": 0.0, "yaw": 0.0}
                if self._enable_demo_pose
                else None
            ),
        )

        self._event_sub = self.create_subscription(
            String,
            "/orchestrator/event",
            self._on_event,
            10,
        )
        self._state_pub = self.create_publisher(String, "/orchestrator/state", 10)
        self._status_pub = self.create_publisher(String, "/orchestrator/status", 10)
        self._last_published_state: str = ""
        self._last_published_status_json: str = ""

        self._timer = None
        if self._publish_rate_hz > 0.0:
            self._timer = self.create_timer(
                1.0 / self._publish_rate_hz,
                lambda: self._publish_snapshot(force=True),
            )

        self._publish_snapshot(force=True)
        self.get_logger().info(
            "Orchestrator runtime skeleton started (state=%s, mode=%s, publish_rate_hz=%.3f, backend=%s, enable_real_motion=%s, enable_demo_pose=%s, nav2_action_name=%s)."
            % (
                self.core.current_state.value,
                self.core.context_snapshot.mode or "",
                self._publish_rate_hz,
                skills_backend,
                str(self._enable_real_motion),
                str(self._enable_demo_pose),
                self._nav2_action_name,
            )
        )

    def _on_event(self, msg: String) -> None:
        status = self.core.step(msg.data)
        self._publish_snapshot(status)

        if not self._debug:
            return

        result = str(status.get("result", ""))
        last_event = str(status.get("last_event", ""))
        summary = str(status.get("chosen_transition_summary", ""))

        if result in ("unknown_event", "policy_blocked"):
            self.get_logger().warn(
                "event=%s result=%s note=%s"
                % (last_event, result, str(status.get("policy_note", "")))
            )
            return

        if result == "no_transition":
            self.get_logger().info(
                "event=%s result=no_transition unknown_guard_count=%s"
                % (last_event, str(status.get("unknown_guard_count", 0)))
            )
            return

        self.get_logger().info(
            "event=%s result=%s transition=%s timeout_key=%s"
            % (
                last_event,
                result,
                summary,
                str(status.get("timeout_key", "")),
            )
        )

    def _publish_snapshot(
        self,
        status: Optional[dict[str, object]] = None,
        *,
        force: bool = False,
    ) -> None:
        if status is None:
            status = self.core.get_status()
        status = dict(status)
        status["enable_real_motion"] = self._enable_real_motion
        status["enable_demo_pose"] = self._enable_demo_pose
        status["nav2_action_name"] = self._nav2_action_name
        status.update(self._extract_last_nav_goal_status_fields())

        current_state = self.core.current_state.value
        status_json = json.dumps(status, sort_keys=True)
        if (
            not force
            and current_state == self._last_published_state
            and status_json == self._last_published_status_json
        ):
            return

        state_msg = String()
        state_msg.data = current_state
        self._state_pub.publish(state_msg)

        status_msg = String()
        status_msg.data = status_json
        self._status_pub.publish(status_msg)
        self._last_published_state = current_state
        self._last_published_status_json = status_json

    def _extract_last_nav_goal_status_fields(self) -> dict[str, object]:
        nav_history = getattr(self.core.skills.nav2, "history", [])
        fallback_entry: dict[str, object] | None = None
        for entry in reversed(nav_history):
            if str(entry.get("request", "")) != "navigate":
                continue
            if fallback_entry is None:
                fallback_entry = entry
            payload = entry.get("goal_payload", {})
            if "goal_payload" not in entry:
                continue
            pose_provided = self._payload_has_pose(payload)
            payload_summary = self._summarize_payload(payload)
            return {
                "last_nav_goal_pose_provided": pose_provided,
                "last_nav_goal_payload_summary": payload_summary,
            }
        if fallback_entry is not None:
            return {
                "last_nav_goal_pose_provided": False,
                "last_nav_goal_payload_summary": "",
            }
        return {
            "last_nav_goal_pose_provided": False,
            "last_nav_goal_payload_summary": "",
        }

    def _payload_has_pose(self, payload: object) -> bool:
        if not isinstance(payload, dict):
            return False
        if isinstance(payload.get("pose_stamped"), dict):
            return True
        required = {"x", "y", "yaw", "frame_id"}
        return required.issubset(set(payload.keys()))

    def _summarize_payload(self, payload: object) -> str:
        if not isinstance(payload, dict):
            return ""
        if isinstance(payload.get("pose_stamped"), dict):
            frame_id = str(payload["pose_stamped"].get("frame_id", ""))
            return f"pose_stamped(frame={frame_id})"
        if self._payload_has_pose(payload):
            frame_id = str(payload.get("frame_id", ""))
            x = payload.get("x", "")
            y = payload.get("y", "")
            yaw = payload.get("yaw", "")
            return f"frame={frame_id},x={x},y={y},yaw={yaw}"
        expr = str(payload.get("expr", ""))
        return expr[:80]


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = OrchestratorRuntimeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
