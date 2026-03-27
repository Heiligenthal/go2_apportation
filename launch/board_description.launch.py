from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    model = LaunchConfiguration("model")
    use_sim_time = LaunchConfiguration("use_sim_time")
    odom_topic = LaunchConfiguration("odom_topic")
    odom_parent_frame = LaunchConfiguration("odom_parent_frame")
    odom_child_frame = LaunchConfiguration("odom_child_frame")
    lidar_frame = LaunchConfiguration("lidar_frame")
    lidar_xyz = LaunchConfiguration("lidar_xyz")
    lidar_rpy = LaunchConfiguration("lidar_rpy")
    camera_frame = LaunchConfiguration("camera_frame")
    camera_xyz = LaunchConfiguration("camera_xyz")
    camera_rpy = LaunchConfiguration("camera_rpy")

    local_launch_dir = Path(__file__).resolve().parent
    board_minimal_launch = str(local_launch_dir / "board_minimal.launch.py")

    board_minimal = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(board_minimal_launch),
        launch_arguments={
            "odom_topic": odom_topic,
            "parent_frame": odom_parent_frame,
            "child_frame": odom_child_frame,
        }.items(),
    )

    robot_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("go2_description"), "launch", "robot_state_publisher.launch.py"]
            )
        ),
        launch_arguments={
            "model": model,
            "use_sim_time": use_sim_time,
            "camera_frame": camera_frame,
            "camera_xyz": camera_xyz,
            "camera_rpy": camera_rpy,
            "lidar_frame": lidar_frame,
            "lidar_xyz": lidar_xyz,
            "lidar_rpy": lidar_rpy,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("model", default_value="urdf/go2.urdf"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("odom_topic", default_value="/utlidar/robot_odom"),
            DeclareLaunchArgument("odom_parent_frame", default_value="odom"),
            DeclareLaunchArgument("odom_child_frame", default_value="base_link"),
            DeclareLaunchArgument("lidar_frame", default_value="lidar_frame"),
            DeclareLaunchArgument("lidar_xyz", default_value="0 0 0"),
            DeclareLaunchArgument("lidar_rpy", default_value="0 0 0"),
            DeclareLaunchArgument("lidar_tf_required", default_value="true"),
            DeclareLaunchArgument("camera_frame", default_value="camera_link"),
            DeclareLaunchArgument("camera_xyz", default_value="0 0 0"),
            DeclareLaunchArgument("camera_rpy", default_value="0 0 0"),
            DeclareLaunchArgument("camera_tf_required", default_value="true"),
            board_minimal,
            LogInfo(
                msg=(
                    "board_description.launch.py: camera_link and lidar_frame are provided by "
                    "go2_description URDF + robot_state_publisher. "
                    "camera_tf_required/lidar_tf_required remain declared only for caller compatibility."
                )
            ),
            robot_description,
        ]
    )
