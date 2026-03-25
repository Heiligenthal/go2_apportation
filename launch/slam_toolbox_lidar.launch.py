from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, ThisLaunchFileDir
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "slam_params_file",
                default_value=PathJoinSubstitution(
                    [ThisLaunchFileDir(), "..", "config", "slam_toolbox_lidar_params.yaml"]
                ),
            ),
            DeclareLaunchArgument("scan_topic", default_value="/scan"),
            DeclareLaunchArgument("base_frame", default_value="base_link"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("map_frame", default_value="map"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            Node(
                package="slam_toolbox",
                executable="async_slam_toolbox_node",
                name="slam_toolbox",
                output="screen",
                parameters=[
                    LaunchConfiguration("slam_params_file"),
                    {
                        "scan_topic": LaunchConfiguration("scan_topic"),
                        "base_frame": LaunchConfiguration("base_frame"),
                        "odom_frame": LaunchConfiguration("odom_frame"),
                        "map_frame": LaunchConfiguration("map_frame"),
                        "mode": "mapping",
                        "publish_tf": True,
                        "use_odometry": True,
                        "transform_publish_period": 0.02,
                        "use_sim_time": LaunchConfiguration("use_sim_time"),
                    },
                ],
            ),
        ]
    )
