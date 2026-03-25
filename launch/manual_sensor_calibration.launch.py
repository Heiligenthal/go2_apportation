from __future__ import annotations

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def _load_community_robot_state_publisher(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time").perform(context)
    package_share = Path(get_package_share_directory("go2_robot_sdk"))
    urdf_path = package_share / "urdf" / "go2.urdf"
    if not urdf_path.is_file():
        raise FileNotFoundError(f"Community Go2 URDF not found: {urdf_path}")

    robot_description = urdf_path.read_text(encoding="utf-8")
    return [
        LogInfo(
            msg=(
                "manual_sensor_calibration.launch.py: using community robot description "
                f"{urdf_path} as default Robot Model source."
            )
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="manual_calibration_robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": robot_description,
                    "use_sim_time": use_sim_time.lower() == "true",
                }
            ],
        ),
    ]


def generate_launch_description() -> LaunchDescription:
    local_launch_dir = Path(__file__).resolve().parent

    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(local_launch_dir / "realsense_board.launch.py")),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
        }.items(),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="manual_sensor_calibration_rviz",
        output="screen",
        arguments=["-d", LaunchConfiguration("rviz_config")],
        condition=IfCondition(LaunchConfiguration("rviz")),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("rviz", default_value="true"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [str(local_launch_dir), "..", "config", "manual_sensor_calibration.rviz"]
                ),
            ),
            OpaqueFunction(function=_load_community_robot_state_publisher),
            realsense_launch,
            rviz_node,
        ]
    )
