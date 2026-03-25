"""
demo.launch.py

All-in-one launch for testing MoveIt WITHOUT real hardware.
Uses joint_state_publisher_gui to fake joint states.

Usage:
  ros2 launch go2_d1_550_moveit_config demo.launch.py

This starts:
  1. robot_state_publisher  (TF + robot_description)
  2. joint_state_publisher  (fake joint states - all joints at 0)
  3. move_group             (MoveIt core)
  4. RViz with Motion Planning panel
"""

from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

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

    robot_description_kinematics = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "kinematics.yaml"
    ])

    ompl_planning_config = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "ompl_planning.yaml"
    ])

    moveit_controllers = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "moveit_controllers.yaml"
    ])

    rviz_config = PathJoinSubstitution([
        FindPackageShare("go2_d1_550_moveit_config"), "config", "moveit.rviz"
    ])

    # ── Nodes ──────────────────────────────────────────────────────────────

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": False}],
    )

    # Publishes all joints at zero - simulates standing Go2 + arm at home
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[{"use_gui": False}],
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            {"robot_description_kinematics": robot_description_kinematics},
            ompl_planning_config,
            moveit_controllers,
            {
                "use_sim_time": False,
                "publish_planning_scene": True,
                "publish_geometry_updates": True,
                "publish_state_updates": True,
                "publish_transforms_updates": True,
            },
        ],
    )

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
        robot_state_publisher,
        joint_state_publisher,
        move_group_node,
        rviz_node,
    ])
