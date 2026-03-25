from __future__ import annotations

from typing import Optional

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


DEFAULT_ODOM_TOPIC = "/utlidar/robot_odom"
DEFAULT_PARENT_FRAME = "odom"
DEFAULT_CHILD_FRAME = "base_link"
DEFAULT_STAMP_SOURCE = "now"
VALID_STAMP_SOURCES = {"now", "message"}


def build_transform_from_odometry(
    odom_msg: Odometry,
    parent_frame: str,
    child_frame: str,
    *,
    stamp_source: str = "message",
    now_stamp=None,
    fallback_parent: str = DEFAULT_PARENT_FRAME,
    fallback_child: str = DEFAULT_CHILD_FRAME,
) -> TransformStamped:
    transform = TransformStamped()
    if stamp_source == "message" or now_stamp is None:
        transform.header.stamp = odom_msg.header.stamp
    else:
        transform.header.stamp = now_stamp
    transform.header.frame_id = (parent_frame or odom_msg.header.frame_id or fallback_parent).strip()
    transform.child_frame_id = (
        child_frame or odom_msg.child_frame_id or fallback_child
    ).strip()

    pose = odom_msg.pose.pose
    transform.transform.translation.x = float(pose.position.x)
    transform.transform.translation.y = float(pose.position.y)
    transform.transform.translation.z = float(pose.position.z)
    transform.transform.rotation = pose.orientation
    return transform


class OdomToTfBroadcaster(Node):
    def __init__(self) -> None:
        super().__init__("odom_to_tf_broadcaster")

        self.declare_parameter("odom_topic", DEFAULT_ODOM_TOPIC)
        self.declare_parameter("parent_frame", DEFAULT_PARENT_FRAME)
        self.declare_parameter("child_frame", DEFAULT_CHILD_FRAME)
        self.declare_parameter("stamp_source", DEFAULT_STAMP_SOURCE)

        self._odom_topic = str(self.get_parameter("odom_topic").value)
        self._parent_frame = str(self.get_parameter("parent_frame").value)
        self._child_frame = str(self.get_parameter("child_frame").value)
        configured_stamp_source = str(self.get_parameter("stamp_source").value).strip().lower()
        if configured_stamp_source not in VALID_STAMP_SOURCES:
            self.get_logger().warning(
                "Invalid stamp_source '%s'; falling back to '%s'."
                % (configured_stamp_source, DEFAULT_STAMP_SOURCE)
            )
            configured_stamp_source = DEFAULT_STAMP_SOURCE
        self._stamp_source = configured_stamp_source
        self._last_bad_stamp_warn_ns = 0

        self._tf_broadcaster = TransformBroadcaster(self)
        self._sub = self.create_subscription(Odometry, self._odom_topic, self._on_odom, 20)

        self.get_logger().info(
            "odom_to_tf_broadcaster active (odom_topic=%s, parent_frame=%s, child_frame=%s, stamp_source=%s)"
            % (self._odom_topic, self._parent_frame, self._child_frame, self._stamp_source)
        )

    def _on_odom(self, msg: Odometry) -> None:
        now_stamp = self.get_clock().now().to_msg()
        if self._stamp_source == "message":
            # Throttled warning: zero message stamp is usually invalid for TF consumers.
            if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
                now_ns = self.get_clock().now().nanoseconds
                if now_ns - self._last_bad_stamp_warn_ns >= 5_000_000_000:
                    self.get_logger().warning(
                        "Received odometry with zero header.stamp while stamp_source=message."
                    )
                    self._last_bad_stamp_warn_ns = now_ns

        transform = build_transform_from_odometry(
            msg,
            parent_frame=self._parent_frame,
            child_frame=self._child_frame,
            stamp_source=self._stamp_source,
            now_stamp=now_stamp,
        )
        self._tf_broadcaster.sendTransform(transform)


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = OdomToTfBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
