from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="go2_person_perception",
                executable="person_surface_node",
                name="person_surface_node",
                output="screen",
            )
        ]
    )
