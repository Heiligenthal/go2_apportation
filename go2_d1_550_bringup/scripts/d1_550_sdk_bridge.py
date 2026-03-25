#!/usr/bin/env python3
"""
d1_550_sdk_bridge.py

Bridge between MoveIt2 and the Unitree D1-550 arm.

Confirmed protocol (from d1_sdk ArmString_.hpp + PubServoInfo_.hpp):

  SEND:    topic  "rt/arm_Command"
           type   unitree_arm::msg::dds_::ArmString_
           struct { std::string data_; }
           value  JSON string:
                  {"seq":N,"address":1,"funcode":1,
                   "data":{"id":SERVO_ID,"angle":DEG,"delay_ms":N}}

  RECEIVE: topic  "current_servo_angle"
           type   unitree_arm::msg::dds_::PubServoInfo_
           struct { float servo0_data_; ... float servo6_data_; }
           unit   degrees (float32)

  EXTRA:   topic  "arm_Feedback"
           type   unitree_arm::msg::dds_::ArmString_
           value  JSON status string

Because unitree_sdk2py does not include the D1-specific DDS types
(unitree_arm::msg::dds_::*), we define lightweight Python dataclasses
that match the CDR wire format and register them manually with CycloneDDS.

Servo ID → joint mapping:
  servo 0 → joint1  (shoulder yaw)
  servo 1 → joint2  (shoulder pitch)
  servo 2 → joint3  (elbow)
  servo 3 → joint4  (wrist roll)
  servo 4 → joint5  (wrist pitch)
  servo 5 → joint6  (wrist yaw)
  servo 6 → gripper_left_joint

Usage:
  ros2 run go2_d1_550_bringup d1_550_sdk_bridge.py \\
    --ros-args -p network_interface:=eth0 -p velocity_scale:=0.1
"""

import rclpy
import rclpy.duration
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup

from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory

import threading
import time
import math
import json
import struct

# ── CycloneDDS Python bindings ────────────────────────────────────────────────
try:
    import cyclonedds.core as dds_core
    import cyclonedds.domain as dds_domain
    import cyclonedds.pub as dds_pub
    import cyclonedds.sub as dds_sub
    import cyclonedds.topic as dds_topic
    from cyclonedds.idl import IdlStruct
    from cyclonedds.idl.types import float32, int8, uint8
    import cyclonedds.idl.annotations as annotate
    DDS_AVAILABLE = True
except ImportError:
    DDS_AVAILABLE = False
    print("[WARN] cyclonedds Python not found - DRY RUN mode")

# ── DDS message type definitions ──────────────────────────────────────────────
# These mirror the C++ structs in ArmString_.hpp and PubServoInfo_.hpp exactly.
# The type name string MUST match getTypeName() in the C++ headers.

if DDS_AVAILABLE:
    @annotate.typename("unitree_arm::msg::dds_::ArmString_")
    @annotate.keyless
    class ArmString(IdlStruct):
        data_: str

    @annotate.typename("unitree_arm::msg::dds_::PubServoInfo_")
    @annotate.keyless
    class PubServoInfo(IdlStruct):
        servo0_data_: float32
        servo1_data_: float32
        servo2_data_: float32
        servo3_data_: float32
        servo4_data_: float32
        servo5_data_: float32
        servo6_data_: float32
else:
    # Dummy classes for dry-run mode
    class ArmString:
        def __init__(self, data_=""): self.data_ = data_
    class PubServoInfo:
        servo0_data_ = servo1_data_ = servo2_data_ = 0.0
        servo3_data_ = servo4_data_ = servo5_data_ = servo6_data_ = 0.0

# ── Protocol constants ────────────────────────────────────────────────────────
TOPIC_CMD      = "rt/arm_Command"
TOPIC_STATE    = "current_servo_angle"
TOPIC_FEEDBACK = "arm_Feedback"

JOINT_TO_SERVO = {
    "joint1":             0,
    "joint2":             1,
    "joint3":             2,
    "joint4":             3,
    "joint5":             4,
    "joint6":             5,
    "gripper_left_joint": 6,
}
ARM_JOINTS     = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]
GRIPPER_JOINTS = ["gripper_left_joint"]

# Gripper conversion: URDF prismatic (0..0.033 m) ↔ servo degrees
# Calibrate GRIPPER_OPEN_DEG on real hardware!
GRIPPER_OPEN_DEG = 30.0
GRIPPER_MAX_M    = 0.033

def rad_to_deg(r: float) -> float: return math.degrees(r)
def deg_to_rad(d: float) -> float: return math.radians(d)

def gripper_m_to_deg(m: float) -> float:
    return max(0.0, min(1.0, m / GRIPPER_MAX_M)) * GRIPPER_OPEN_DEG

def gripper_deg_to_m(d: float) -> float:
    return max(0.0, min(1.0, d / GRIPPER_OPEN_DEG)) * GRIPPER_MAX_M


# ── Bridge node ───────────────────────────────────────────────────────────────
class D1550SDKBridge(Node):

    def __init__(self):
        super().__init__("d1_550_sdk_bridge")

        self.declare_parameter("network_interface",     "eth0")
        self.declare_parameter("publish_rate_hz",        50.0)
        self.declare_parameter("velocity_scale",          0.1)
        self.declare_parameter("inter_joint_delay_ms",     20)
        self.declare_parameter("dry_run",           not DDS_AVAILABLE)

        self.iface     = self.get_parameter("network_interface").value
        self.rate      = self.get_parameter("publish_rate_hz").value
        self.vel_scale = self.get_parameter("velocity_scale").value
        self.delay_ms  = self.get_parameter("inter_joint_delay_ms").value
        self.dry_run   = self.get_parameter("dry_run").value

        # Current servo angles in degrees (updated from PubServoInfo_ callbacks)
        self._servo_deg = {name: 0.0 for name in JOINT_TO_SERVO}
        self._seq       = 0
        self._lock      = threading.Lock()

        # DDS handles
        self._dp        = None   # DomainParticipant
        self._writer    = None   # DataWriter for ArmString_
        self._reader    = None   # DataReader for PubServoInfo_
        self._fb_reader = None   # DataReader for arm_Feedback

        # ROS publisher: joint states → robot_state_publisher → /tf
        self.js_pub = self.create_publisher(JointState, "/joint_states", 10)

        cb = ReentrantCallbackGroup()

        # MoveIt2 action servers – names must match moveit_controllers.yaml
        ActionServer(self, FollowJointTrajectory,
            "/d1_550_arm_controller/follow_joint_trajectory",
            execute_callback=self._exec_arm,
            goal_callback=lambda r: GoalResponse.ACCEPT,
            cancel_callback=lambda gh: CancelResponse.ACCEPT,
            callback_group=cb)

        ActionServer(self, FollowJointTrajectory,
            "/d1_550_gripper_controller/follow_joint_trajectory",
            execute_callback=self._exec_gripper,
            goal_callback=lambda r: GoalResponse.ACCEPT,
            cancel_callback=lambda gh: CancelResponse.ACCEPT,
            callback_group=cb)

        if not self.dry_run:
            self._init_dds()
        else:
            self.get_logger().warn("DRY RUN - no hardware commands sent")

        # Timer: publish joint states at configured rate
        self.create_timer(1.0 / self.rate, self._pub_joint_states)

        # Timer: poll DDS readers (PubServoInfo_ + arm_Feedback)
        if not self.dry_run:
            self.create_timer(1.0 / self.rate, self._poll_dds)

        self.get_logger().info(
            f"D1-550 bridge ready | iface={self.iface} "
            f"dry_run={self.dry_run} vel_scale={self.vel_scale} "
            f"delay_ms={self.delay_ms}"
        )

    # ── DDS setup ──────────────────────────────────────────────────────────

    def _init_dds(self):
        try:
            # Create DDS domain participant
            # D1-550 uses CycloneDDS domain 0 on the network interface
            # Set CYCLONEDDS_URI env var to select the interface if needed:
            #   export CYCLONEDDS_URI='<CycloneDDS><Domain><General>
            #     <Interfaces><NetworkInterface name="eth0"/></Interfaces>
            #   </General></Domain></CycloneDDS>'
            self._dp = dds_domain.DomainParticipant(0)

            # Publisher for commands
            cmd_topic = dds_topic.Topic(self._dp, TOPIC_CMD, ArmString)
            self._writer = dds_pub.DataWriter(
                dds_pub.Publisher(self._dp), cmd_topic)

            # Subscriber for joint state feedback
            state_topic = dds_topic.Topic(self._dp, TOPIC_STATE, PubServoInfo)
            self._reader = dds_sub.DataReader(
                dds_sub.Subscriber(self._dp), state_topic)

            # Subscriber for arm feedback JSON
            fb_topic = dds_topic.Topic(self._dp, TOPIC_FEEDBACK, ArmString)
            self._fb_reader = dds_sub.DataReader(
                dds_sub.Subscriber(self._dp), fb_topic)

            self.get_logger().info(f"DDS initialized on domain 0 (iface={self.iface})")

        except Exception as e:
            self.get_logger().error(f"DDS init failed: {e} → dry run")
            self.dry_run = True

    # ── DDS polling (replaces callbacks - cyclonedds Python uses read()) ──

    def _poll_dds(self):
        """Poll DDS readers for new data (called by timer)."""
        if self._reader:
            try:
                samples = self._reader.read(10)
                for sample in samples:
                    if sample.sample_info.valid_data:
                        self._on_servo_info(sample)
            except Exception as e:
                self.get_logger().debug(f"State poll error: {e}")

        if self._fb_reader:
            try:
                samples = self._fb_reader.read(10)
                for sample in samples:
                    if sample.sample_info.valid_data:
                        self.get_logger().debug(f"arm_Feedback: {sample.data_}")
            except Exception:
                pass

    def _on_servo_info(self, sample: PubServoInfo):
        """Update internal servo state from PubServoInfo_ message."""
        with self._lock:
            self._servo_deg["joint1"]             = float(sample.servo0_data_)
            self._servo_deg["joint2"]             = float(sample.servo1_data_)
            self._servo_deg["joint3"]             = float(sample.servo2_data_)
            self._servo_deg["joint4"]             = float(sample.servo3_data_)
            self._servo_deg["joint5"]             = float(sample.servo4_data_)
            self._servo_deg["joint6"]             = float(sample.servo5_data_)
            self._servo_deg["gripper_left_joint"] = float(sample.servo6_data_)

    # ── Joint state publishing ─────────────────────────────────────────────

    def _pub_joint_states(self):
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()

        with self._lock:
            angles = dict(self._servo_deg)

        # Arm joints: degrees → radians
        for name in ARM_JOINTS:
            js.name.append(name)
            js.position.append(deg_to_rad(angles[name]))
            js.velocity.append(0.0)

        # Gripper: degrees → meters (URDF prismatic)
        gm = gripper_deg_to_m(angles["gripper_left_joint"])
        for name in ["gripper_left_joint", "gripper_right_joint"]:
            js.name.append(name)
            js.position.append(gm)
            js.velocity.append(0.0)

        self.js_pub.publish(js)

    # ── Send command ───────────────────────────────────────────────────────

    def _send_servo(self, joint_name: str, value: float):
        """
        Send one servo command to the D1-550.
        value: radians (arm joints) or meters (gripper).
        """
        servo_id = JOINT_TO_SERVO.get(joint_name)
        if servo_id is None:
            return

        deg = (gripper_m_to_deg(value)
               if joint_name == "gripper_left_joint"
               else rad_to_deg(value))

        self._seq += 1
        payload = json.dumps({
            "seq":     self._seq,
            "address": 1,
            "funcode": 1,
            "data": {
                "id":       servo_id,
                "angle":    round(deg, 3),
                "delay_ms": self.delay_ms,
            }
        })

        self.get_logger().debug(f"→ {payload}")

        # Optimistically update internal state (real update comes via PubServoInfo_)
        with self._lock:
            self._servo_deg[joint_name] = deg

        if self.dry_run or self._writer is None:
            return

        try:
            # ArmString_ has a single field: data_ (str)
            msg = ArmString(data_=payload)
            self._writer.write(msg)
        except Exception as e:
            self.get_logger().error(f"DDS write error [{joint_name}]: {e}")

    def _send_waypoint(self, joint_names: list, positions: list):
        """Send all joints for one trajectory waypoint sequentially."""
        for name, pos in zip(joint_names, positions):
            if name in JOINT_TO_SERVO:
                self._send_servo(name, pos)
                time.sleep(self.delay_ms / 1000.0)

    # ── Trajectory execution ───────────────────────────────────────────────

    async def _exec_arm(self, goal_handle):
        return await self._exec_traj(goal_handle)

    async def _exec_gripper(self, goal_handle):
        return await self._exec_traj(goal_handle)

    async def _exec_traj(self, goal_handle):
        traj   = goal_handle.request.trajectory
        result = FollowJointTrajectory.Result()

        if not traj.points:
            goal_handle.succeed()
            result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
            return result

        self.get_logger().info(
            f"Executing {len(traj.points)} waypoints | "
            f"joints={list(traj.joint_names)} | scale={self.vel_scale}"
        )

        t0 = self.get_clock().now()

        for i, pt in enumerate(traj.points):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.error_code = FollowJointTrajectory.Result.GOAL_TOLERANCE_VIOLATED
                return result

            # Send waypoint
            self._send_waypoint(list(traj.joint_names), list(pt.positions))

            # Respect trajectory timing scaled by velocity_scale
            t_target = (pt.time_from_start.sec +
                        pt.time_from_start.nanosec * 1e-9) / self.vel_scale
            elapsed  = (self.get_clock().now() - t0).nanoseconds * 1e-9
            wait     = t_target - elapsed
            if wait > 0.001:
                time.sleep(wait)

            # Publish feedback to MoveIt
            fb = FollowJointTrajectory.Feedback()
            fb.joint_names = list(traj.joint_names)
            with self._lock:
                fb.actual.positions = [
                    deg_to_rad(self._servo_deg.get(n, 0.0))
                    if n != "gripper_left_joint"
                    else gripper_deg_to_m(self._servo_deg.get(n, 0.0))
                    for n in traj.joint_names
                ]
            goal_handle.publish_feedback(fb)

        goal_handle.succeed()
        result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
        self.get_logger().info("Trajectory complete ✓")
        return result

    def destroy_node(self):
        if self._dp:
            self._dp.close()
        super().destroy_node()


# ── Entry point ────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = D1550SDKBridge()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
