from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .interfaces import ManipulationSkillInterface, Nav2SkillInterface
from .manipulation_skill_stub import ManipulationSkillStub
from .nav2_skill_real_client import Nav2SkillRealClient
from .nav2_skill_stub import Nav2SkillStub
from .real_backend_placeholder import (
    ManipulationSkillRealPlaceholder,
    Nav2SkillRealPlaceholder,
)


@dataclass
class SkillBundle:
    nav2: Nav2SkillInterface = field(default_factory=Nav2SkillStub)
    manip: ManipulationSkillInterface = field(default_factory=ManipulationSkillStub)
    backend: str = "stub"


def create_skill_bundle(
    backend: str,
    *,
    node: Any = None,
    enable_real_motion: bool = False,
    nav2_action_name: str = "/navigate_to_pose",
) -> SkillBundle:
    normalized = backend.strip().lower()
    if normalized == "stub":
        return SkillBundle(backend="stub")

    if normalized in ("ros", "mock"):
        if node is None:
            raise ValueError("skills backend 'ros/mock' requires a ROS node instance")
        from .manipulation_skill_ros_client import ManipulationSkillRosClient
        from .nav2_skill_ros_client import Nav2SkillRosClient

        return SkillBundle(
            nav2=Nav2SkillRosClient(node=node),
            manip=ManipulationSkillRosClient(node=node),
            backend=normalized,
        )

    if normalized in ("real_nav2", "real"):
        if node is None:
            raise ValueError("skills backend 'real_nav2/real' requires a ROS node instance")
        return SkillBundle(
            nav2=Nav2SkillRealClient(
                node=node,
                action_name=nav2_action_name,
                enable_real_motion=enable_real_motion,
            ),
            manip=ManipulationSkillStub(),
            backend="real_nav2",
        )

    if normalized == "real_placeholder":
        return SkillBundle(
            nav2=Nav2SkillRealPlaceholder(),
            manip=ManipulationSkillRealPlaceholder(),
            backend="real_placeholder",
        )

    raise ValueError(f"unknown skills backend '{backend}'")
