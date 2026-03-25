from __future__ import annotations

from dataclasses import dataclass

from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

from .contracts import (
    LOCAL_PERSON_POSE_INPUT_TOPIC,
    LOCAL_PERSON_VISIBLE_INPUT_TOPIC,
    PERSON_LAST_SEEN_TOPIC,
    PERSON_POSE_FRAME,
    PERSON_POSE_TOPIC,
    PERSON_VISIBLE_TOPIC,
)
from .person_surface_logic import LocalPoseInput, decide_pose_input, decide_visible_input


@dataclass
class PersonObservation:
    visible: bool
    pose: PoseStamped | None = None


class PersonSurfaceNode(Node):
    """Minimal local adapter for the frozen person surface from Document 002."""

    def __init__(self) -> None:
        super().__init__("person_surface_node")

        self.declare_parameter("visible_publish_rate_hz", 2.0)

        self._visible_publisher = self.create_publisher(Bool, PERSON_VISIBLE_TOPIC, 10)
        self._pose_publisher = self.create_publisher(PoseStamped, PERSON_POSE_TOPIC, 10)
        self._last_seen_publisher = self.create_publisher(PoseStamped, PERSON_LAST_SEEN_TOPIC, 10)

        self._last_visible = False
        self._last_seen_pose: PoseStamped | None = None

        self._pose_input_subscription = self.create_subscription(
            PoseStamped,
            LOCAL_PERSON_POSE_INPUT_TOPIC,
            self._on_local_pose_input,
            10,
        )
        self._visible_input_subscription = self.create_subscription(
            Bool,
            LOCAL_PERSON_VISIBLE_INPUT_TOPIC,
            self._on_local_visible_input,
            10,
        )

        publish_rate_hz = float(self.get_parameter("visible_publish_rate_hz").value)
        publish_period_s = 0.5 if publish_rate_hz <= 0.0 else 1.0 / publish_rate_hz
        self.create_timer(publish_period_s, self._publish_visible_state)

        self.get_logger().info(
            "Person surface ready: local adapter inputs feed frozen person topics without control logic."
        )

    def apply_observation(self, observation: PersonObservation) -> None:
        """Future upstream adapters can call this without changing the frozen outputs."""

        self._last_visible = bool(observation.visible)

        if observation.pose is None:
            return

        normalized_pose = PoseStamped()
        normalized_pose.header = observation.pose.header
        normalized_pose.header.frame_id = PERSON_POSE_FRAME
        normalized_pose.pose = observation.pose.pose

        self._pose_publisher.publish(normalized_pose)
        self._last_seen_pose = normalized_pose
        self._last_seen_publisher.publish(self._last_seen_pose)

    def _on_local_pose_input(self, msg: PoseStamped) -> None:
        decision = decide_pose_input(
            LocalPoseInput(frame_id=msg.header.frame_id),
            previous_visible=self._last_visible,
        )
        self._last_visible = decision.visible
        if not decision.publish_pose:
            return
        self.apply_observation(PersonObservation(visible=True, pose=msg))

    def _on_local_visible_input(self, msg: Bool) -> None:
        decision = decide_visible_input(msg.data)
        self._last_visible = decision.visible

    def _publish_visible_state(self) -> None:
        msg = Bool()
        msg.data = self._last_visible
        self._visible_publisher.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = PersonSurfaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
