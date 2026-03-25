from __future__ import annotations

from nav_msgs.msg import Odometry

from src.go2_tf_tools.go2_tf_tools.odom_to_tf_broadcaster import (
    build_transform_from_odometry,
)


def _sample_odom() -> Odometry:
    msg = Odometry()
    msg.header.stamp.sec = 12
    msg.header.stamp.nanosec = 345
    msg.header.frame_id = "odom"
    msg.child_frame_id = "base_link"
    msg.pose.pose.position.x = 1.25
    msg.pose.pose.position.y = -0.5
    msg.pose.pose.position.z = 0.1
    msg.pose.pose.orientation.x = 0.0
    msg.pose.pose.orientation.y = 0.0
    msg.pose.pose.orientation.z = 0.7
    msg.pose.pose.orientation.w = 0.7
    return msg


def test_build_transform_from_odometry_uses_configured_frames() -> None:
    odom = _sample_odom()

    tf_msg = build_transform_from_odometry(
        odom,
        parent_frame="odom_custom",
        child_frame="base_custom",
    )

    assert tf_msg.header.stamp.sec == 12
    assert tf_msg.header.stamp.nanosec == 345
    assert tf_msg.header.frame_id == "odom_custom"
    assert tf_msg.child_frame_id == "base_custom"
    assert tf_msg.transform.translation.x == 1.25
    assert tf_msg.transform.translation.y == -0.5
    assert tf_msg.transform.translation.z == 0.1
    assert tf_msg.transform.rotation.z == 0.7
    assert tf_msg.transform.rotation.w == 0.7


def test_build_transform_from_odometry_uses_message_frames_when_params_empty() -> None:
    odom = _sample_odom()

    tf_msg = build_transform_from_odometry(
        odom,
        parent_frame="",
        child_frame="",
    )

    assert tf_msg.header.frame_id == "odom"
    assert tf_msg.child_frame_id == "base_link"
