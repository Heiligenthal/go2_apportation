from __future__ import annotations

from collections import deque
import time
from typing import Optional

import rclpy
from go2_apportation_msgs.action import PickObject
from go2_apportation_msgs.srv import ReleaseObject
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from .scenario_config import PICK_SCENARIOS, RELEASE_SCENARIOS, normalize_scenario


class MockManipulationServer(Node):
    def __init__(self) -> None:
        super().__init__("mock_manipulation_server")

        self.declare_parameter("pick_action_name", "/manipulation/pick")
        self.declare_parameter("pick_scenario", "success")
        self.declare_parameter("pick_result_delay_s", 0.3)
        self.declare_parameter("pick_accept_goal", True)
        self.declare_parameter("release_service_name", "/manipulation/release")
        self.declare_parameter("release_scenario", "success")
        self.declare_parameter("release_result_delay_s", 0.1)

        self._pick_action_name = str(self.get_parameter("pick_action_name").value)
        pick_scenario_raw = str(self.get_parameter("pick_scenario").value)
        self._pick_scenario, pick_default = normalize_scenario(
            pick_scenario_raw,
            allowed=PICK_SCENARIOS,
            default="success",
        )
        self._pick_delay_s = float(self.get_parameter("pick_result_delay_s").value)
        self._pick_accept_goal = bool(self.get_parameter("pick_accept_goal").value)
        self._release_service_name = str(self.get_parameter("release_service_name").value)
        release_scenario_raw = str(self.get_parameter("release_scenario").value)
        self._release_scenario, release_default = normalize_scenario(
            release_scenario_raw,
            allowed=RELEASE_SCENARIOS,
            default="success",
        )
        self._release_delay_s = float(self.get_parameter("release_result_delay_s").value)
        self._pick_goal_seq = 0
        self._accepted_pick_goal_ids: deque[int] = deque()

        self._pick_server = ActionServer(
            self,
            PickObject,
            self._pick_action_name,
            goal_callback=self._on_pick_goal,
            cancel_callback=self._on_pick_cancel,
            execute_callback=self._on_pick_execute,
        )
        self._release_server = self.create_service(
            ReleaseObject,
            self._release_service_name,
            self._on_release,
        )

        if pick_default:
            self.get_logger().warn(
                "Unknown pick_scenario '%s', fallback to 'success'." % pick_scenario_raw
            )
        if release_default:
            self.get_logger().warn(
                "Unknown release_scenario '%s', fallback to 'success'." % release_scenario_raw
            )
        self.get_logger().info(
            "Mock manipulation server running (pick=%s scenario=%s delay=%.2f, release=%s scenario=%s delay=%.2f)"
            % (
                self._pick_action_name,
                self._pick_scenario,
                self._pick_delay_s,
                self._release_service_name,
                self._release_scenario,
                self._release_delay_s,
            )
        )

    def _on_pick_goal(self, _goal_request: PickObject.Goal) -> GoalResponse:
        self._pick_goal_seq += 1
        goal_id = self._pick_goal_seq
        self.get_logger().info(
            "pick goal received id=%d scenario=%s on %s"
            % (goal_id, self._pick_scenario, self._pick_action_name)
        )
        if not self._pick_accept_goal:
            self.get_logger().info("pick goal rejected id=%d" % goal_id)
            return GoalResponse.REJECT
        self._accepted_pick_goal_ids.append(goal_id)
        return GoalResponse.ACCEPT

    def _on_pick_cancel(self, _goal_handle: object) -> CancelResponse:
        self.get_logger().info("pick cancel received")
        return CancelResponse.ACCEPT

    def _on_pick_execute(self, goal_handle: object) -> PickObject.Result:
        goal_id = self._accepted_pick_goal_ids.popleft() if self._accepted_pick_goal_ids else -1
        feedback = PickObject.Feedback()
        feedback.stage = 1
        feedback.stage_text = "MOCK_START"
        goal_handle.publish_feedback(feedback)

        result = PickObject.Result()
        if self._pick_scenario == "hang":
            while rclpy.ok():
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    result.success = False
                    result.result_code = 7
                    result.message = "cancelled"
                    self.get_logger().info("pick result=canceled id=%d scenario=hang" % goal_id)
                    return result
                time.sleep(0.05)

        end_time = time.monotonic() + max(0.0, self._pick_delay_s)
        while rclpy.ok() and time.monotonic() < end_time:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.success = False
                result.result_code = 7
                result.message = "cancelled"
                self.get_logger().info(
                    "pick result=canceled id=%d scenario=%s" % (goal_id, self._pick_scenario)
                )
                return result
            time.sleep(0.02)

        if self._pick_scenario == "success":
            goal_handle.succeed()
            result.success = True
            result.result_code = 0
            result.message = "mock success"
            self.get_logger().info("pick result=succeeded id=%d scenario=success" % goal_id)
            return result

        goal_handle.abort()
        result.success = False
        result.result_code = 5
        result.message = "mock failure"
        self.get_logger().info("pick result=aborted id=%d scenario=%s" % (goal_id, self._pick_scenario))
        return result

    def _on_release(
        self,
        request: ReleaseObject.Request,
        response: ReleaseObject.Response,
    ) -> ReleaseObject.Response:
        self.get_logger().info(
            "release request received on %s (mode=%d, verify_open=%s, scenario=%s)"
            % (
                self._release_service_name,
                int(request.release_mode),
                str(request.verify_open),
                self._release_scenario,
            )
        )
        time.sleep(max(0.0, self._release_delay_s))

        if self._release_scenario == "hang":
            while rclpy.ok():
                time.sleep(0.2)
            response.success = False
            response.result_code = 9
            response.message = "mock hang interrupted by shutdown"
            return response

        response.success = self._release_scenario == "success"
        response.result_code = 0 if response.success else 2
        response.message = "mock success" if response.success else "mock failure"
        self.get_logger().info(
            "release result=%s scenario=%s"
            % ("success" if response.success else "failure", self._release_scenario)
        )
        return response


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = MockManipulationServer()
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
