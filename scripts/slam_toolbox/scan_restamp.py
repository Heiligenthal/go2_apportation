#!/usr/bin/env python3
from __future__ import annotations

import sys

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ScanRestamp(Node):
    def __init__(self, in_topic: str, out_topic: str):
        super().__init__("scan_restamp")
        self.in_topic = in_topic
        self.out_topic = out_topic
        self.rx_count = 0
        self.tx_count = 0
        self.logged_first_msg = False

        self.pub = self.create_publisher(LaserScan, out_topic, qos_profile_sensor_data)
        self.sub = self.create_subscription(
            LaserScan, in_topic, self.cb, qos_profile_sensor_data
        )
        self.stats_timer = self.create_timer(2.0, self.log_stats)

        self.get_logger().info(
            f"scan_restamp started: input='{self.in_topic}' output='{self.out_topic}' qos=sensor_data"
        )

    def cb(self, msg: LaserScan) -> None:
        self.rx_count += 1
        if not self.logged_first_msg:
            self.logged_first_msg = True
            self.get_logger().info(
                "first scan received: "
                f"frame_id='{msg.header.frame_id}' stamp={msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d}"
            )
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)
        self.tx_count += 1

    def log_stats(self) -> None:
        self.get_logger().info(
            f"scan_restamp counters: received={self.rx_count} published={self.tx_count}"
        )


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: scan_restamp.py <input_topic> <output_topic>", file=sys.stderr)
        return 2

    rclpy.init()
    node = ScanRestamp(sys.argv[1], sys.argv[2])
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
