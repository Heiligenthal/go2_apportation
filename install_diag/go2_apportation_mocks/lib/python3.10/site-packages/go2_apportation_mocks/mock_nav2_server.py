from __future__ import annotations

from collections import deque
import time
from typing import Optional

import rclpy
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from .scenario_config import NAV2_SCENARIOS, normalize_scenario


class MockNavigateToPoseServer(Node):
    def __init__(self) -> None:
        super().__init__("mock_nav2_server")

        self.declare_parameter("action_name", "/navigate_to_pose")
        self.declare_parameter("scenario", "success")
        self.declare_parameter("result_delay_s", 0.2)
        self.declare_parameter("accept_goal", True)

        self._action_name = str(self.get_parameter("action_name").value)
        scenario_raw = str(self.get_parameter("scenario").value)
        self._scenario, used_default = normalize_scenario(
            scenario_raw,
            allowed=NAV2_SCENARIOS,
            default="success",
        )
        self._delay_s = float(self.get_parameter("result_delay_s").value)
        self._accept_goal = bool(self.get_parameter("accept_goal").value)
        self._goal_seq = 0
        self._accepted_goal_ids: deque[int] = deque()

        self._server = ActionServer(
            self,
            NavigateToPose,
            self._action_name,
            goal_callback=self._on_goal,
            cancel_callback=self._on_cancel,
            execute_callback=self._on_execute,
        )

        if used_default:
            self.get_logger().warn(
                "Unknown scenario '%s', fallback to 'success'." % scenario_raw
            )
        self.get_logger().info(
            "Mock NavigateToPose server running at %s (scenario=%s, delay=%.2f, accept_goal=%s)"
            % (self._action_name, self._scenario, self._delay_s, str(self._accept_goal))
        )

    def _on_goal(self, _goal_request: NavigateToPose.Goal) -> GoalResponse:
        self._goal_seq += 1
        goal_id = self._goal_seq
        self.get_logger().info(
            "GOAL_RECEIVED id=%d scenario=%s action_name=%s"
            % (goal_id, self._scenario, self._action_name)
        )
        if not self._accept_goal:
            self.get_logger().info("goal rejected id=%d" % goal_id)
            return GoalResponse.REJECT
        self._accepted_goal_ids.append(goal_id)
        return GoalResponse.ACCEPT

    def _on_cancel(self, _goal_handle: object) -> CancelResponse:
        self.get_logger().info("CANCEL_RECEIVED")
        return CancelResponse.ACCEPT

    def _on_execute(self, goal_handle: object) -> NavigateToPose.Result:
        goal_id = self._accepted_goal_ids.popleft() if self._accepted_goal_ids else -1
        result = NavigateToPose.Result()

        if self._scenario == "hang":
            while rclpy.ok():
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    if hasattr(result, "error_code"):
                        result.error_code = 2
                    if hasattr(result, "error_msg"):
                        result.error_msg = "cancelled"
                    self.get_logger().info("RESULT_CANCELED id=%d scenario=hang" % goal_id)
                    return result
                time.sleep(0.05)

        end_time = time.monotonic() + max(0.0, self._delay_s)
        while rclpy.ok() and time.monotonic() < end_time:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                if hasattr(result, "error_code"):
                    result.error_code = 2
                if hasattr(result, "error_msg"):
                    result.error_msg = "cancelled"
                self.get_logger().info(
                    "RESULT_CANCELED id=%d scenario=%s" % (goal_id, self._scenario)
                )
                return result
            time.sleep(0.02)

        if self._scenario == "success":
            goal_handle.succeed()
            if hasattr(result, "error_code"):
                result.error_code = 0
            if hasattr(result, "error_msg"):
                result.error_msg = "success"
            self.get_logger().info("RESULT_SUCCEEDED id=%d scenario=success" % goal_id)
            return result

        goal_handle.abort()
        if hasattr(result, "error_code"):
            result.error_code = 1
        if hasattr(result, "error_msg"):
            result.error_msg = "mock failure"
        self.get_logger().info("RESULT_ABORTED id=%d scenario=%s" % (goal_id, self._scenario))
        return result


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = MockNavigateToPoseServer()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
