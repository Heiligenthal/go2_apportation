#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2


class PointCloudThrottle(Node):
    def __init__(
        self,
        input_topic: str,
        output_topic: str,
        every_n: int,
        label: str,
        *,
        stamp_mode: str,
    ) -> None:
        super().__init__(f"manual_pointcloud_throttle_{label}")
        self._input_topic = input_topic
        self._output_topic = output_topic
        self._every_n = max(every_n, 1)
        self._label = label
        self._stamp_mode = stamp_mode
        self._message_count = 0
        self._published_count = 0

        self._publisher = self.create_publisher(PointCloud2, self._output_topic, qos_profile_sensor_data)
        self._subscription = self.create_subscription(
            PointCloud2,
            self._input_topic,
            self._on_cloud,
            qos_profile_sensor_data,
        )

        self.get_logger().info(
            "manual_pointcloud_throttle active "
            f"(label={self._label}, input_topic={self._input_topic}, output_topic={self._output_topic}, "
            f"every_n={self._every_n}, stamp_mode={self._stamp_mode})"
        )

    def _on_cloud(self, msg: PointCloud2) -> None:
        self._message_count += 1
        if self._message_count % self._every_n != 0:
            return
        msg_out = copy.deepcopy(msg)
        if self._stamp_mode == "now":
            msg_out.header.stamp = self.get_clock().now().to_msg()
        self._publisher.publish(msg_out)
        self._published_count += 1
        if self._published_count <= 3:
            self.get_logger().info(
                f"{self._label}: forwarded cloud #{self._published_count} "
                f"frame_id={msg_out.header.frame_id} stamp_mode={self._stamp_mode}"
            )


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Throttle PointCloud2 for manual RViz calibration.")
    parser.add_argument("--input-topic", required=True)
    parser.add_argument("--output-topic", required=True)
    parser.add_argument("--every-n", type=int, default=2)
    parser.add_argument("--label", default="cloud")
    parser.add_argument("--stamp-mode", choices=["preserve", "now"], default="now")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    rclpy.init(args=argv)
    node = PointCloudThrottle(
        args.input_topic,
        args.output_topic,
        args.every_n,
        args.label,
        stamp_mode=args.stamp_mode,
    )
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
