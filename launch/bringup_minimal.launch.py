# file: bringup_minimal.launch.py
# Minimal bringup plan (ROS2 Humble) for your pipeline:
# - robot_state_publisher (URDF for base_link->sensor frames + arm frames)
# - Unitree bridge (publishes odom->base_link, joint_states, etc.)
# - RealSense driver
# - rgbd_sync + rtabmap
# - Nav2
#
# NOTE: This is a structural template; replace package/executable names with your actual ones.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    urdf_path = LaunchConfiguration("urdf_path")
    nav2_params = LaunchConfiguration("nav2_params")
    rtabmap_params = LaunchConfiguration("rtabmap_params")
    realsense_params = LaunchConfiguration("realsense_params")

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("urdf_path", default_value=""),  # e.g. <your_pkg>/urdf/go2.urdf
        DeclareLaunchArgument("nav2_params", default_value=""), # path to nav2_params.yaml
        DeclareLaunchArgument("rtabmap_params", default_value=""), # path to rtabmap_params.yaml
        DeclareLaunchArgument("realsense_params", default_value=""), # path to realsense.yaml

        # 1) TF static tree from URDF (base_link->camera_link/imu_link/lidar_frame/arm...)
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                # Use robot_description from file; if you generate via xacro, do it here.
                # "robot_description": Command(["xacro ", urdf_path]),
            }],
            # If you don't use xacro Command, load robot_description in another way.
        ),

        # 2) Unitree bridge / base bringup (placeholder)
        # Replace with your actual Unitree ROS2 bringup launch or node.
        # IncludeLaunchDescription(
        #   PythonLaunchDescriptionSource([FindPackageShare("unitree_go2_bringup"), "/launch/bringup.launch.py"]),
        #   launch_arguments={"use_sim_time": use_sim_time}.items()
        # ),

        # 3) RealSense driver
        Node(
            package="realsense2_camera",
            executable="realsense2_camera_node",
            name="realsense2_camera",
            output="screen",
            parameters=[realsense_params, {"use_sim_time": use_sim_time}],
        ),

        # 4) RTAB-Map: rgbd_sync + rtabmap (assumes these executables exist in rtabmap_ros)
        Node(
            package="rtabmap_sync",
            executable="rgbd_sync",
            name="rgbd_sync",
            output="screen",
            parameters=[rtabmap_params, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="rtabmap_slam",
            executable="rtabmap",
            name="rtabmap",
            output="screen",
            parameters=[rtabmap_params, {"use_sim_time": use_sim_time}],
        ),

        # 5) Nav2 bringup (nav2_bringup)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare("nav2_bringup"), "launch", "bringup_launch.py"])
            ),
            launch_arguments={
                "use_sim_time": use_sim_time,
                "params_file": nav2_params,
            }.items(),
        ),
    ])

