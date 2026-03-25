from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, ThisLaunchFileDir
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    # Use ROS2-parseable baseline params file.
    # Topic defaults remain explicit launch args.
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "rtabmap_params_file",
                default_value=PathJoinSubstitution(
                    [ThisLaunchFileDir(), "..", "config", "rtabmap_ros2_params.yaml"]
                ),
            ),
            DeclareLaunchArgument(
                "rgb_topic",
                default_value="/camera/realsense2_camera/color/image_raw",
            ),
            DeclareLaunchArgument(
                "depth_topic",
                default_value="/camera/realsense2_camera/aligned_depth_to_color/image_raw",
            ),
            DeclareLaunchArgument(
                "camera_info_topic",
                default_value="/camera/realsense2_camera/color/camera_info",
            ),
            DeclareLaunchArgument("scan_topic", default_value="/scan"),
            DeclareLaunchArgument("base_frame", default_value="base_link"),
            DeclareLaunchArgument("odom_frame", default_value="odom"),
            DeclareLaunchArgument("map_frame", default_value="map"),
            DeclareLaunchArgument("map_topic", default_value="/map"),
            DeclareLaunchArgument("database_path", default_value="~/.ros/rtabmap.db"),
            Node(
                package="rtabmap_sync",
                executable="rgbd_sync",
                name="rgbd_sync",
                output="screen",
                remappings=[
                    ("rgb/image", LaunchConfiguration("rgb_topic")),
                    ("depth/image", LaunchConfiguration("depth_topic")),
                    ("rgb/camera_info", LaunchConfiguration("camera_info_topic")),
                ],
                parameters=[
                    LaunchConfiguration("rtabmap_params_file"),
                    {
                        "rgb_topic": LaunchConfiguration("rgb_topic"),
                        "depth_topic": LaunchConfiguration("depth_topic"),
                        "camera_info_topic": LaunchConfiguration("camera_info_topic"),
                    },
                ],
            ),
            Node(
                package="rtabmap_slam",
                executable="rtabmap",
                name="rtabmap",
                output="screen",
                remappings=[
                    ("scan", LaunchConfiguration("scan_topic")),
                    ("map", LaunchConfiguration("map_topic")),
                ],
                parameters=[
                    LaunchConfiguration("rtabmap_params_file"),
                    {
                        "base_frame_id": LaunchConfiguration("base_frame"),
                        "odom_frame_id": LaunchConfiguration("odom_frame"),
                        "map_frame_id": LaunchConfiguration("map_frame"),
                        "subscribe_scan": True,
                        "scan_topic": LaunchConfiguration("scan_topic"),
                        "database_path": LaunchConfiguration("database_path"),
                        "Mem/IncrementalMemory": "false",
                    },
                ],
            ),
        ]
    )
