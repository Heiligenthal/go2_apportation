from __future__ import annotations

from typing import Optional

import rclpy
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ZeroJointStatePublisher(Node):
    def __init__(self) -> None:
        super().__init__("zero_joint_state_publisher")
        self.declare_parameter(
            "joint_names",
            value=[],
            descriptor=ParameterDescriptor(type=ParameterType.PARAMETER_STRING_ARRAY),
        )
        self.declare_parameter("publish_rate_hz", 10.0)

        self._joint_names = [str(name) for name in self.get_parameter("joint_names").value]
        publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        self._publisher = self.create_publisher(JointState, "/joint_states", 10)
        period = 1.0 / max(publish_rate_hz, 1.0)
        self._timer = self.create_timer(period, self._publish_zero_joint_state)

        self.get_logger().info(
            "zero_joint_state_publisher active (joint_count=%d, publish_rate_hz=%.2f)"
            % (len(self._joint_names), publish_rate_hz)
        )

    def _publish_zero_joint_state(self) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self._joint_names)
        msg.position = [0.0 for _ in self._joint_names]
        msg.velocity = []
        msg.effort = []
        self._publisher.publish(msg)


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = ZeroJointStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
