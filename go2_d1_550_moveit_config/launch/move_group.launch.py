"""
move_group.launch.py

Starts the MoveIt2 move_group node for the Go2 + D1-550.
This is the core MoveIt process - run this on the robot or companion PC.

Usage:
  ros2 launch go2_d1_550_moveit_config move_group.launch.py

Prerequisites:
  - robot_state_publisher must be running (publishing /robot_description + /tf)
  - joint_states must be published (from hardware interface or SDK bridge)
  - arm controller action server must be available
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Robot description from combined xacro
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([
            FindPackageShare("go2_d1_550_description"),
            "urdf", "go2_d1_550.urdf.xacro"
        ]),
    ])
    robot_description = {"robot_description": robot_description_content}

    # MoveIt config paths
    moveit_config_pkg = get_package_share_directory("go2_d1_550_moveit_config")

    robot_description_semantic = {
        "robot_description_semantic":
            open(os.path.join(moveit_config_pkg, "config", "go2_d1_550.srdf")).read()
    }

    robot_description_kinematics = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "kinematics.yaml"
    ])

    robot_description_planning = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "joint_limits.yaml"
    ])

    ompl_planning_config = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "ompl_planning.yaml"
    ])

    moveit_controllers = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "moveit_controllers.yaml"
    ])

    # move_group node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            {"robot_description_kinematics": robot_description_kinematics},
            {"robot_description_planning": robot_description_planning},
            ompl_planning_config,
            moveit_controllers,
            {
                "use_sim_time": False,
                # Planning scene monitor settings
                "publish_planning_scene": True,
                "publish_geometry_updates": True,
                "publish_state_updates": True,
                "publish_transforms_updates": True,
                "monitor_dynamics": False,
                # Planning parameters
                "planning_scene_monitor_options": {
                    "name": "planning_scene_monitor",
                    "robot_description": "robot_description",
                    "joint_state_topic": "/joint_states",
                    "attached_collision_object_topic": "/move_group/planning_scene_monitor",
                    "publish_planning_scene_topic": "/move_group/publish_planning_scene",
                    "monitored_planning_scene_topic": "/monitored_planning_scene",
                    "wait_for_initial_state_timeout": 10.0,
                },
            },
        ],
    )

    return LaunchDescription([
        move_group_node,
    ])
