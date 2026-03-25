from __future__ import annotations

import os
import shutil

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _create_robot_state_publisher(context: object) -> list[Node]:
    package_share = get_package_share_directory("go2_description")
    model_relative_path = LaunchConfiguration("model").perform(context)
    model_path = os.path.join(package_share, model_relative_path)

    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            "Model file does not exist: "
            + model_path
            + " (expected path relative to go2_description share)"
        )

    if model_path.endswith(".xacro"):
        xacro_executable = shutil.which("xacro")
        if xacro_executable is None:
            raise RuntimeError(
                "xacro model requested, but 'xacro' executable is unavailable. "
                "Use a plain URDF model path or install xacro."
            )
        robot_description = ParameterValue(
            Command([xacro_executable, " ", model_path]),
            value_type=str,
        )
    else:
        with open(model_path, "r", encoding="utf-8") as urdf_file:
            robot_description = urdf_file.read()

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": robot_description,
                    "use_sim_time": LaunchConfiguration("use_sim_time"),
                }
            ],
        )
    ]


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value="urdf/go2.urdf",
                description="URDF or xacro path relative to go2_description share",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation clock",
            ),
            OpaqueFunction(function=_create_robot_state_publisher),
        ]
    )
