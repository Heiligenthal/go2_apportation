"""
moveit_rviz.launch.py

Starts RViz with the MoveIt Motion Planning panel.
Run this alongside move_group.launch.py for interactive planning.

Usage:
  ros2 launch go2_d1_550_moveit_config moveit_rviz.launch.py
"""

from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

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

    robot_description_kinematics = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "kinematics.yaml"
    ])

    rviz_config = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "moveit.rviz"
    ])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        parameters=[
            robot_description,
            robot_description_semantic,
            {"robot_description_kinematics": robot_description_kinematics},
            {"use_sim_time": False},
        ],
        output="screen",
    )

    return LaunchDescription([
        rviz_node,
    ])
