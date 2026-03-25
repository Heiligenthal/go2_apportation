from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class D1550ReusePoints:
    """Implementation-local reuse points from the existing D1-550 stack."""

    move_group_package: str = "go2_d1_550_moveit_config"
    description_package: str = "go2_d1_550_description"
    bringup_package: str = "go2_d1_550_bringup"
    arm_group: str = "arm"
    gripper_group: str = "gripper"
    end_effector: str = "gripper_ee"
    arm_controller_action: str = "/d1_550_arm_controller/follow_joint_trajectory"
    gripper_controller_action: str = "/d1_550_gripper_controller/follow_joint_trajectory"
    move_group_launch: str = "go2_d1_550_moveit_config/launch/move_group.launch.py"


D1_REUSE_POINTS = D1550ReusePoints()

# These SRDF names are reused only as local implementation hooks.
# They are intentionally not exported as global mission semantics.
LOCAL_NAMED_STATES: tuple[str, ...] = ("home", "ready", "stow", "open", "closed")
