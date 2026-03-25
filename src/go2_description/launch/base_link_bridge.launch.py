from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _create_static_bridge(context: object) -> list[Node]:
    parent_frame = LaunchConfiguration("parent_frame").perform(context).strip()
    child_frame = LaunchConfiguration("child_frame").perform(context).strip()
    xyz_values = LaunchConfiguration("xyz").perform(context).strip().split()
    rpy_values = LaunchConfiguration("rpy").perform(context).strip().split()

    if len(xyz_values) != 3:
        raise RuntimeError("Launch arg 'xyz' must contain exactly 3 values: 'x y z'")
    if len(rpy_values) != 3:
        raise RuntimeError("Launch arg 'rpy' must contain exactly 3 values: 'roll pitch yaw'")

    return [
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="base_link_to_base_static_bridge",
            output="screen",
            arguments=[
                xyz_values[0],
                xyz_values[1],
                xyz_values[2],
                rpy_values[0],
                rpy_values[1],
                rpy_values[2],
                parent_frame,
                child_frame,
            ],
        )
    ]


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("parent_frame", default_value="base_link"),
            DeclareLaunchArgument("child_frame", default_value="base"),
            DeclareLaunchArgument("xyz", default_value="0 0 0"),
            DeclareLaunchArgument("rpy", default_value="0 0 0"),
            OpaqueFunction(function=_create_static_bridge),
        ]
    )
