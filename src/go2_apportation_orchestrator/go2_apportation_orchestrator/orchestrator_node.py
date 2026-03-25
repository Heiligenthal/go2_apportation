from __future__ import annotations

"""Legacy phase-1 stub node.

This file intentionally remains separate from the document-near runtime path in
orchestrator_runtime_core.py / orchestrator_runtime_node.py. It should not be
read as the authoritative mission-flow implementation.
"""

from typing import Optional

import rclpy
from rclpy.node import Node

from .state_contracts import Event, MissionState, OrchestratorSnapshot


class OrchestratorStubNode(Node):
    """Phase-1 skeleton only.

    This node intentionally avoids mission logic, action execution, or cmd_vel control.
    It only provides a typed placeholder for the future orchestrator implementation.
    """

    def __init__(self) -> None:
        super().__init__("orchestrator_stub")
        self.snapshot = OrchestratorSnapshot()
        self.declare_parameter("cmd_vel_ownership_mode", self.snapshot.cmd_vel_ownership_mode.value)
        self.get_logger().info(
            "Phase-1 orchestrator stub started (state=%s, cmd_vel ownership=%s)." % (
                self.snapshot.state.value,
                self.snapshot.cmd_vel_ownership_mode.value,
            )
        )

    def handle_event(self, event: Event) -> None:
        """Placeholder event entrypoint. No transition logic in Phase 1."""
        self.get_logger().info("Received event stub: %s (no transition logic implemented yet)" % event.value)

    def transition_to(self, new_state: MissionState, reason: Optional[str] = None) -> None:
        """Explicit transition setter for future integration tests / scaffolding."""
        old_state = self.snapshot.state
        self.snapshot.state = new_state
        suffix = "" if reason is None else f" reason={reason}"
        self.get_logger().info("Stub transition: %s -> %s%s" % (old_state.value, new_state.value, suffix))


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = OrchestratorStubNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
