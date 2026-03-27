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
                        # Keep the productive board path on the project's canonical
                        # RGB-D topics for RTAB-Map localization.
                        "enable_color": True,
                        "enable_depth": True,
                        "enable_infra1": False,
                        "enable_infra2": False,
                        "enable_sync": True,
                        "color_width": 640,
                        "color_height": 480,
                        "color_fps": 30,
                        "depth_width": 640,
                        "depth_height": 480,
                        "depth_fps": 30,
                        "align_depth.enable": True,
                        "pointcloud.enable": True,
                        "publish_tf": True,
                    },
                ],
            ),
        ]
    )
