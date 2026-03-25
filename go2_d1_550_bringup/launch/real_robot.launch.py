"""
real_robot.launch.py

Full bringup for Go2 EDU + D1-550 with real hardware.

Usage:
  ros2 launch go2_d1_550_bringup real_robot.launch.py network_interface:=eth0

This starts:
  1. robot_state_publisher  (TF + robot_description)
  2. d1_550_sdk_bridge      (SDK ↔ ROS2 bridge: joint_states + action server)
  3. move_group             (MoveIt core)
  4. RViz (optional, set rviz:=false to disable)

IMPORTANT before running on real hardware:
  - Verify arm mounting offset in go2_d1_550.urdf.xacro matches physical setup
  - Check network_interface name (ip a)
  - Set velocity_scale low (0.05-0.1) for first runs
  - Have emergency stop ready
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # ── Arguments ──────────────────────────────────────────────────────────
    network_interface_arg = DeclareLaunchArgument(
        "network_interface", default_value="eth0",
        description="Network interface connected to Go2/D1-550 (check with: ip a)"
    )
    velocity_scale_arg = DeclareLaunchArgument(
        "velocity_scale", default_value="0.1",
        description="Velocity scaling factor (0.0-1.0). Start low!"
    )
    rviz_arg = DeclareLaunchArgument(
        "rviz", default_value="true",
        description="Launch RViz"
    )

    # ── Robot description ──────────────────────────────────────────────────
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([
            FindPackageShare("go2_d1_550_description"),
            "urdf", "go2_d1_550.urdf.xacro"
        ]),
    ])
    robot_description = {"robot_description": robot_description_content}

    moveit_config_pkg = get_package_share_directory("go2_d1_550_moveit_config")

    robot_description_semantic = {
        "robot_description_semantic":
            open(os.path.join(moveit_config_pkg, "config", "go2_d1_550.srdf")).read()
    }

    # ── Nodes ──────────────────────────────────────────────────────────────

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": False}],
    )

    sdk_bridge = Node(
        package="go2_d1_550_bringup",
        executable="d1_550_sdk_bridge.py",
        output="screen",
        parameters=[{
            "network_interface": LaunchConfiguration("network_interface"),
            "velocity_scale":    LaunchConfiguration("velocity_scale"),
            "publish_rate_hz":   50.0,
            "dry_run":           False,
        }],
    )

    # MoveIt move_group
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("go2_d1_550_moveit_config"),
                "launch", "move_group.launch.py"
            ])
        ]),
    )

    # RViz with MoveIt panel
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("go2_d1_550_moveit_config"),
                "launch", "moveit_rviz.launch.py"
            ])
        ]),
        condition=IfCondition(LaunchConfiguration("rviz")),
    )

    return LaunchDescription([
        network_interface_arg,
        velocity_scale_arg,
        rviz_arg,
        robot_state_publisher,
        sdk_bridge,
        move_group_launch,
        rviz_launch,
    ])
