from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    odom_topic = LaunchConfiguration("odom_topic")
    parent_frame = LaunchConfiguration("parent_frame")
    child_frame = LaunchConfiguration("child_frame")

    # Optional /utlidar/robot_odom -> /odom relay is intentionally not started
    # here to avoid adding a new runtime dependency (e.g. topic_tools).
    relay_note = LogInfo(
        msg=(
            "board_minimal.launch.py: odom relay disabled "
            "(no additional relay dependency in R1)."
        )
    )

    tf_adapter = Node(
        package="go2_tf_tools",
        executable="odom_to_tf_broadcaster",
        name="odom_to_tf_broadcaster",
        output="screen",
        parameters=[
            {
                "odom_topic": odom_topic,
                "parent_frame": parent_frame,
                "child_frame": child_frame,
            }
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("odom_topic", default_value="/utlidar/robot_odom"),
            DeclareLaunchArgument("parent_frame", default_value="odom"),
            DeclareLaunchArgument("child_frame", default_value="base_link"),
            relay_note,
            tf_adapter,
        ]
    )

