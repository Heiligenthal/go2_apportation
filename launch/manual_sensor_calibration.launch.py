from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def _load_filtered_repo_robot_description() -> tuple[str, list[str]]:
    package_share = Path(get_package_share_directory("go2_description"))
    urdf_path = package_share / "urdf" / "go2.urdf"
    if not urdf_path.is_file():
        raise FileNotFoundError(f"Repo Go2 URDF not found: {urdf_path}")

    tree = ET.parse(urdf_path)
    root = tree.getroot()
    sensor_links = {"camera_link", "lidar_frame"}

    removable_joints = []
    removable_links = []

    movable_joint_names: list[str] = []
    for joint in root.findall("joint"):
        if joint.get("type") not in {"fixed", "floating"} and joint.get("name"):
            movable_joint_names.append(joint.get("name"))
        child = joint.find("child")
        if child is not None and child.get("link") in sensor_links:
            removable_joints.append(joint)

    for link in root.findall("link"):
        if link.get("name") in sensor_links:
            removable_links.append(link)

    for joint in removable_joints:
        root.remove(joint)
    for link in removable_links:
        root.remove(link)

    return ET.tostring(root, encoding="unicode"), movable_joint_names


def _load_repo_robot_state_publisher(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time").perform(context)
    robot_description, movable_joint_names = _load_filtered_repo_robot_description()

    return [
        LogInfo(
            msg=(
                "manual_sensor_calibration.launch.py: using repo go2_description/urdf/go2.urdf "
                "as default Robot Model source, with camera_link/lidar_frame removed via XML filtering for manual TF override. "
                "The URDF itself now provides base_link as the parent of the relevant sensor and IMU frames."
            )
        ),
        LogInfo(
            msg=(
                "manual_sensor_calibration.launch.py: using manual RealSense profile "
                "config/realsense_manual_calibration.yaml for reduced RViz calibration load."
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
        Node(
            package="go2_tf_tools",
            executable="zero_joint_state_publisher",
            name="manual_calibration_zero_joint_state_publisher",
            output="screen",
            parameters=[
                {
                    "use_sim_time": use_sim_time.lower() == "true",
                    "joint_names": movable_joint_names,
                    "publish_rate_hz": 10.0,
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
            "realsense_params_file": PathJoinSubstitution(
                [str(local_launch_dir), "..", "config", "realsense_manual_calibration.yaml"]
            ),
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
            DeclareLaunchArgument("rviz", default_value="false"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [str(local_launch_dir), "..", "config", "manual_sensor_calibration.rviz"]
                ),
            ),
            LogInfo(
                msg=(
                    "manual_sensor_calibration.launch.py: running in a base_link-local visualization mode; "
                    "manual calibration does not start a live odom->base_link broadcaster. "
                    "External RViz on the Ubuntu laptop is the productive default. "
                    "No extra base_link->base bridge is started here; the repo URDF now carries that relationship."
                )
            ),
            OpaqueFunction(function=_load_repo_robot_state_publisher),
            realsense_launch,
            rviz_node,
        ]
    )
