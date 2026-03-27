from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, ThisLaunchFileDir
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "realsense_params_file",
                default_value=PathJoinSubstitution(
                    [ThisLaunchFileDir(), "..", "config", "realsense.yaml"]
                ),
                description="Path to RealSense ROS2 parameter YAML",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
            ),
            Node(
                package="realsense2_camera",
                executable="realsense2_camera_node",
                name="realsense2_camera",
                output="screen",
                parameters=[
                    LaunchConfiguration("realsense_params_file"),
                    {
                        "use_sim_time": LaunchConfiguration("use_sim_time"),
                        "publish_tf": True,
                    },
                ],
            ),
        ]
    )
