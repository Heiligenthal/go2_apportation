"""Tracking adapters for shared-surface boundaries."""

from dataclasses import dataclass
from typing import Tuple

from .contracts import DEFAULT_CONTRACTS

try:
    from go2_apportation_msgs.msg import (
        Detection3DArray,
        InterceptGoal,
        ObjectState,
        PredictedRegion,
        ThrowStatus,
    )
except ImportError:  # pragma: no cover - import-safe for pure python tests.
    Detection3DArray = None  # type: ignore[assignment]
    InterceptGoal = None  # type: ignore[assignment]
    ObjectState = None  # type: ignore[assignment]
    PredictedRegion = None  # type: ignore[assignment]
    ThrowStatus = None  # type: ignore[assignment]


@dataclass(frozen=True)
class InternalTrackingMeasurement:
    """Owner-local tracking measurement candidate."""

    frame_id: str
    center_xyz: Tuple[float, float, float]
    confidence: float
    stamp_s: float


@dataclass(frozen=True)
class InternalPredictionCandidate:
    """Owner-local conservative prediction/intercept candidate."""

    frame_id: str
    center_xyz: Tuple[float, float, float]
    confidence: float
    stamp_s: float
    valid_for_s: float
    size_xyz: Tuple[float, float, float]
    approach_radius_m: float
    goal_tolerance_m: float
    is_dynamic_estimate: bool = True


def accept_public_detection_input(message):
    """Accept the READY public Detection3DArray input."""

    if Detection3DArray is None:
        raise RuntimeError("go2_apportation_msgs/Detection3DArray is not available in this environment")
    if not isinstance(message, Detection3DArray):
        raise TypeError("expected go2_apportation_msgs/Detection3DArray for /tracking/detections3d_fast")
    return message


def _set_stamp(stamp, seconds: float) -> None:
    """Populate builtin_interfaces/Time fields from floating-point seconds."""

    normalized = max(0.0, float(seconds))
    stamp.sec = int(normalized)
    stamp.nanosec = int((normalized - int(normalized)) * 1_000_000_000)


def _set_duration(duration, seconds: float) -> None:
    """Populate builtin_interfaces/Duration fields from floating-point seconds."""

    normalized = max(0.0, float(seconds))
    duration.sec = int(normalized)
    duration.nanosec = int((normalized - int(normalized)) * 1_000_000_000)


def build_object_state_msg(measurement: InternalTrackingMeasurement):
    """Build the READY public ObjectState in the odom-led tracking frame."""

    if ObjectState is None:
        raise RuntimeError("go2_apportation_msgs/ObjectState is not available in this environment")
    message = ObjectState()
    message.header.frame_id = measurement.frame_id or DEFAULT_CONTRACTS.state_frame
    if hasattr(message.header, "stamp"):
        _set_stamp(message.header.stamp, measurement.stamp_s)
    message.pose.pose.position.x = float(measurement.center_xyz[0])
    message.pose.pose.position.y = float(measurement.center_xyz[1])
    message.pose.pose.position.z = float(measurement.center_xyz[2])
    message.pose.pose.orientation.w = 1.0
    message.twist.twist.linear.x = 0.0
    message.twist.twist.linear.y = 0.0
    message.twist.twist.linear.z = 0.0
    message.twist.twist.angular.x = 0.0
    message.twist.twist.angular.y = 0.0
    message.twist.twist.angular.z = 0.0
    return message


def build_throw_status_msg(status: str, *, frame_id: str = DEFAULT_CONTRACTS.state_frame, stamp_s: float = 0.0):
    """Build the READY public ThrowStatus using only frozen public states."""

    if ThrowStatus is None:
        raise RuntimeError("go2_apportation_msgs/ThrowStatus is not available in this environment")
    status_map = {
        "IDLE": ThrowStatus.IDLE,
        "HELD": ThrowStatus.HELD,
        "RELEASE_SUSPECTED": ThrowStatus.RELEASE_SUSPECTED,
        "THROWN": ThrowStatus.THROWN,
        "LANDED": ThrowStatus.LANDED,
        "LOST": ThrowStatus.LOST,
    }
    if status not in status_map:
        raise ValueError(f"unsupported public throw status '{status}'")
    message = ThrowStatus()
    message.header.frame_id = frame_id
    if hasattr(message.header, "stamp"):
        _set_stamp(message.header.stamp, stamp_s)
    message.status = status_map[status]
    return message


def build_predicted_region_msg(candidate: InternalPredictionCandidate):
    """Build the READY public PredictedRegion with conservative odom-frame semantics."""

    if PredictedRegion is None:
        raise RuntimeError("go2_apportation_msgs/PredictedRegion is not available in this environment")
    message = PredictedRegion()
    message.header.frame_id = candidate.frame_id or DEFAULT_CONTRACTS.state_frame
    if hasattr(message.header, "stamp"):
        _set_stamp(message.header.stamp, candidate.stamp_s)
    message.center.position.x = float(candidate.center_xyz[0])
    message.center.position.y = float(candidate.center_xyz[1])
    message.center.position.z = float(candidate.center_xyz[2])
    message.center.orientation.w = 1.0
    message.size.x = float(candidate.size_xyz[0])
    message.size.y = float(candidate.size_xyz[1])
    message.size.z = float(candidate.size_xyz[2])
    message.confidence = float(candidate.confidence)
    _set_duration(message.valid_for, candidate.valid_for_s)
    return message


def build_intercept_goal_msg(candidate: InternalPredictionCandidate):
    """Build the READY public InterceptGoal without controller semantics."""

    if InterceptGoal is None:
        raise RuntimeError("go2_apportation_msgs/InterceptGoal is not available in this environment")
    message = InterceptGoal()
    frame_id = candidate.frame_id or DEFAULT_CONTRACTS.state_frame
    message.header.frame_id = frame_id
    if hasattr(message.header, "stamp"):
        _set_stamp(message.header.stamp, candidate.stamp_s)
    message.target_pose.header.frame_id = frame_id
    if hasattr(message.target_pose.header, "stamp"):
        _set_stamp(message.target_pose.header.stamp, candidate.stamp_s)
    message.target_pose.pose.position.x = float(candidate.center_xyz[0])
    message.target_pose.pose.position.y = float(candidate.center_xyz[1])
    message.target_pose.pose.position.z = float(candidate.center_xyz[2])
    message.target_pose.pose.orientation.w = 1.0
    message.approach_radius_m = float(candidate.approach_radius_m)
    message.goal_tolerance_m = float(candidate.goal_tolerance_m)
    message.confidence = float(candidate.confidence)
    _set_duration(message.valid_for, candidate.valid_for_s)
    message.is_dynamic_estimate = bool(candidate.is_dynamic_estimate)
    return message
