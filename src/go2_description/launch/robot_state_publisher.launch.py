from __future__ import annotations

import os
import shutil
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _normalize_triplet(value: str, argument_name: str) -> str:
    parts = value.split()
    if len(parts) != 3:
        raise RuntimeError(
            f"robot_state_publisher.launch.py: {argument_name} must have 3 space-separated numbers."
        )
    return " ".join(parts)


def _rename_link(root: ET.Element, old_name: str, new_name: str) -> None:
    if old_name == new_name:
        return

    found = False
    for link in root.findall("link"):
        if link.get("name") == old_name:
            link.set("name", new_name)
            found = True

    if not found:
        raise RuntimeError(
            f"robot_state_publisher.launch.py: expected link '{old_name}' in URDF."
        )

    for joint in root.findall("joint"):
        parent = joint.find("parent")
        child = joint.find("child")
        if parent is not None and parent.get("link") == old_name:
            parent.set("link", new_name)
        if child is not None and child.get("link") == old_name:
            child.set("link", new_name)


def _patch_fixed_joint(
    root: ET.Element,
    *,
    joint_name: str,
    parent_link: str,
    child_link: str,
    xyz: str,
    rpy: str,
) -> None:
    for joint in root.findall("joint"):
        if joint.get("name") != joint_name:
            continue

        origin = joint.find("origin")
        parent = joint.find("parent")
        child = joint.find("child")
        if origin is None or parent is None or child is None:
            raise RuntimeError(
                f"robot_state_publisher.launch.py: joint '{joint_name}' misses origin/parent/child."
            )

        origin.set("xyz", xyz)
        origin.set("rpy", rpy)
        parent.set("link", parent_link)
        child.set("link", child_link)
        return

    raise RuntimeError(
        f"robot_state_publisher.launch.py: expected joint '{joint_name}' in URDF."
    )


def _load_and_patch_urdf(
    model_path: str,
    *,
    camera_frame: str,
    camera_xyz: str,
    camera_rpy: str,
    lidar_frame: str,
    lidar_xyz: str,
    lidar_rpy: str,
) -> str:
    root = ET.parse(model_path).getroot()

    _rename_link(root, "camera_link", camera_frame)
    _rename_link(root, "lidar_frame", lidar_frame)

    _patch_fixed_joint(
        root,
        joint_name="camera_link_joint",
        parent_link="base_link",
        child_link=camera_frame,
        xyz=_normalize_triplet(camera_xyz, "camera_xyz"),
        rpy=_normalize_triplet(camera_rpy, "camera_rpy"),
    )
    _patch_fixed_joint(
        root,
        joint_name="lidar_frame_joint",
        parent_link="base_link",
        child_link=lidar_frame,
        xyz=_normalize_triplet(lidar_xyz, "lidar_xyz"),
        rpy=_normalize_triplet(lidar_rpy, "lidar_rpy"),
    )

    return ET.tostring(root, encoding="unicode")


def _create_robot_state_publisher(context: object) -> list[object]:
    package_share = get_package_share_directory("go2_description")
    model_relative_path = LaunchConfiguration("model").perform(context)
    model_path = os.path.join(package_share, model_relative_path)
    camera_frame = LaunchConfiguration("camera_frame").perform(context)
    camera_xyz = LaunchConfiguration("camera_xyz").perform(context)
    camera_rpy = LaunchConfiguration("camera_rpy").perform(context)
    lidar_frame = LaunchConfiguration("lidar_frame").perform(context)
    lidar_xyz = LaunchConfiguration("lidar_xyz").perform(context)
    lidar_rpy = LaunchConfiguration("lidar_rpy").perform(context)

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
        robot_description = _load_and_patch_urdf(
            model_path,
            camera_frame=camera_frame,
            camera_xyz=camera_xyz,
            camera_rpy=camera_rpy,
            lidar_frame=lidar_frame,
            lidar_xyz=lidar_xyz,
            lidar_rpy=lidar_rpy,
        )

    return [
        LogInfo(
            msg=(
                "robot_state_publisher.launch.py: model="
                + model_path
                + f" camera_frame={camera_frame} camera_xyz='{camera_xyz}' camera_rpy='{camera_rpy}'"
                + f" lidar_frame={lidar_frame} lidar_xyz='{lidar_xyz}' lidar_rpy='{lidar_rpy}'"
            )
        ),
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
        ),
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
            DeclareLaunchArgument("camera_frame", default_value="camera_link"),
            DeclareLaunchArgument("camera_xyz", default_value="0.2203 0 0.1225"),
            DeclareLaunchArgument("camera_rpy", default_value="0 0.05 0"),
            DeclareLaunchArgument("lidar_frame", default_value="lidar_frame"),
            DeclareLaunchArgument("lidar_xyz", default_value="0.28945 0 -0.046825"),
            DeclareLaunchArgument("lidar_rpy", default_value="0 2.8782 0"),
            OpaqueFunction(function=_create_robot_state_publisher),
        ]
    )
