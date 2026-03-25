from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _make_lidar_static_tf(context, *args, **kwargs):
    xyz = LaunchConfiguration("lidar_xyz").perform(context).split()
    rpy = LaunchConfiguration("lidar_rpy").perform(context).split()
    lidar_frame = LaunchConfiguration("lidar_frame").perform(context)

    if len(xyz) != 3 or len(rpy) != 3:
        raise RuntimeError(
            "board_description.launch.py: lidar_xyz and lidar_rpy must each have 3 space-separated numbers."
        )

    return [
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="base_link_to_lidar_static_tf",
            output="screen",
            condition=IfCondition(LaunchConfiguration("lidar_tf_required")),
            arguments=[
                xyz[0],
                xyz[1],
                xyz[2],
                rpy[0],
                rpy[1],
                rpy[2],
                "base_link",
                lidar_frame,
            ],
        )
    ]


def _make_camera_static_tf(context, *args, **kwargs):
    xyz = LaunchConfiguration("camera_xyz").perform(context).split()
    rpy = LaunchConfiguration("camera_rpy").perform(context).split()
    camera_frame = LaunchConfiguration("camera_frame").perform(context)

    if len(xyz) != 3 or len(rpy) != 3:
        raise RuntimeError(
            "board_description.launch.py: camera_xyz and camera_rpy must each have 3 space-separated numbers."
        )

    return [
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="base_link_to_camera_static_tf",
            output="screen",
            condition=IfCondition(LaunchConfiguration("camera_tf_required")),
            arguments=[
                xyz[0],
                xyz[1],
                xyz[2],
                rpy[0],
                rpy[1],
                rpy[2],
                "base_link",
                camera_frame,
            ],
        )
    ]


def generate_launch_description() -> LaunchDescription:
    model = LaunchConfiguration("model")
    use_sim_time = LaunchConfiguration("use_sim_time")
    bridge_parent_frame = LaunchConfiguration("bridge_parent_frame")
    bridge_child_frame = LaunchConfiguration("bridge_child_frame")
    odom_topic = LaunchConfiguration("odom_topic")
    odom_parent_frame = LaunchConfiguration("odom_parent_frame")
    odom_child_frame = LaunchConfiguration("odom_child_frame")
    lidar_frame = LaunchConfiguration("lidar_frame")
    lidar_xyz = LaunchConfiguration("lidar_xyz")
    lidar_rpy = LaunchConfiguration("lidar_rpy")
    lidar_tf_required = LaunchConfiguration("lidar_tf_required")
    camera_frame = LaunchConfiguration("camera_frame")
    camera_xyz = LaunchConfiguration("camera_xyz")
    camera_rpy = LaunchConfiguration("camera_rpy")
    camera_tf_required = LaunchConfiguration("camera_tf_required")

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
        }.items(),
    )

    base_link_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("go2_description"), "launch", "base_link_bridge.launch.py"]
            )
        ),
        launch_arguments={
            "parent_frame": bridge_parent_frame,
            "child_frame": bridge_child_frame,
            "xyz": "0 0 0",
            "rpy": "0 0 0",
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("model", default_value="urdf/go2.urdf"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("odom_topic", default_value="/utlidar/robot_odom"),
            DeclareLaunchArgument("odom_parent_frame", default_value="odom"),
            DeclareLaunchArgument("odom_child_frame", default_value="base_link"),
            DeclareLaunchArgument("bridge_parent_frame", default_value="base_link"),
            DeclareLaunchArgument("bridge_child_frame", default_value="base"),
            DeclareLaunchArgument("lidar_frame", default_value="utlidar_lidar"),
            DeclareLaunchArgument("lidar_xyz", default_value="0 0 0"),
            DeclareLaunchArgument("lidar_rpy", default_value="0 0 0"),
            DeclareLaunchArgument("lidar_tf_required", default_value="true"),
            DeclareLaunchArgument("camera_frame", default_value="camera_link"),
            DeclareLaunchArgument("camera_xyz", default_value="0 0 0"),
            DeclareLaunchArgument("camera_rpy", default_value="0 0 0"),
            DeclareLaunchArgument("camera_tf_required", default_value="true"),
            board_minimal,
            robot_description,
            base_link_bridge,
            OpaqueFunction(function=_make_lidar_static_tf),
            OpaqueFunction(function=_make_camera_static_tf),
        ]
    )
