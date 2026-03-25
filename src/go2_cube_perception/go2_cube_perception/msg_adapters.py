"""Adapters for external message publication boundaries."""

from dataclasses import dataclass
from typing import Tuple

from . import frames, topics

try:
    from geometry_msgs.msg import PoseStamped
    from std_msgs.msg import Bool
    from go2_apportation_msgs.msg import Detection3D, Detection3DArray
except ImportError:  # pragma: no cover - import-safe for pure python tests.
    PoseStamped = None  # type: ignore[assignment]
    Bool = None  # type: ignore[assignment]
    Detection3D = None  # type: ignore[assignment]
    Detection3DArray = None  # type: ignore[assignment]

BLOCKED_BY_H06 = "BLOCKED_BY_H06"


class BlockedByH06Error(RuntimeError):
    """Raised when an external shared-surface decision is still owned by H06."""


@dataclass(frozen=True)
class InternalFastDetectionCandidate:
    """Owner-local fast detection candidate."""

    frame_id: str
    center_xyz: Tuple[float, float, float]
    confidence: float
    source_hint: str
    stamp_s: float = 0.0
    class_id: int = 1


@dataclass(frozen=True)
class InternalMapFastMeasurement:
    """Owner-local map-based FAST measurement for tracking/filtering only."""

    frame_id: str
    position_map_xyz: Tuple[float, float, float]
    measurement_confidence: float
    stamp_s: float
    source_frame: str
    bbox_center_norm_xy: Tuple[float, float]
    centered: bool


@dataclass(frozen=True)
class InternalPrecisePoseCandidate:
    """Owner-local precise pose candidate."""

    frame_id: str
    center_xyz: Tuple[float, float, float]
    face_normal: Tuple[float, float, float]
    edge_axis_mod_pi: Tuple[float, float, float]
    confidence: float
    orientation_xyzw: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    stamp_s: float = 0.0


def build_object_visible_msg(is_visible: bool):
    """Build the READY object-visible public message."""

    if Bool is None:
        raise RuntimeError("std_msgs/Bool is not available in this environment")
    msg = Bool()
    msg.data = bool(is_visible)
    return msg


def build_detections3d_fast_msg(candidate: InternalFastDetectionCandidate):
    """Build the READY public Detection3DArray message in odom."""

    if Detection3DArray is None or Detection3D is None:
        raise RuntimeError("go2_apportation_msgs Detection3DArray is not available in this environment")
    message = Detection3DArray()
    message.header.frame_id = candidate.frame_id or frames.FAST_OUTPUT_FRAME
    if hasattr(message.header, "stamp"):
        seconds = max(0.0, float(candidate.stamp_s))
        message.header.stamp.sec = int(seconds)
        message.header.stamp.nanosec = int((seconds - int(seconds)) * 1_000_000_000)
    detection = Detection3D()
    detection.pose.pose.position.x = candidate.center_xyz[0]
    detection.pose.pose.position.y = candidate.center_xyz[1]
    detection.pose.pose.position.z = candidate.center_xyz[2]
    detection.pose.pose.orientation.w = 1.0
    detection.confidence = float(candidate.confidence)
    detection.class_id = int(candidate.class_id)
    message.detections.append(detection)
    return message


def build_object_pose_msg(candidate: InternalPrecisePoseCandidate):
    """Build the READY public object pose message."""

    if PoseStamped is None:
        raise RuntimeError("geometry_msgs/PoseStamped is not available in this environment")
    message = PoseStamped()
    message.header.frame_id = candidate.frame_id or frames.PRECISE_OUTPUT_FRAME
    if hasattr(message.header, "stamp"):
        seconds = max(0.0, float(candidate.stamp_s))
        message.header.stamp.sec = int(seconds)
        message.header.stamp.nanosec = int((seconds - int(seconds)) * 1_000_000_000)
    message.pose.position.x = candidate.center_xyz[0]
    message.pose.position.y = candidate.center_xyz[1]
    message.pose.position.z = candidate.center_xyz[2]
    message.pose.orientation.x = candidate.orientation_xyzw[0]
    message.pose.orientation.y = candidate.orientation_xyzw[1]
    message.pose.orientation.z = candidate.orientation_xyzw[2]
    message.pose.orientation.w = candidate.orientation_xyzw[3]
    return message


def build_object_last_seen_msg(candidate: InternalPrecisePoseCandidate):
    """Build the READY public object last-seen message in map."""

    if PoseStamped is None:
        raise RuntimeError("geometry_msgs/PoseStamped is not available in this environment")
    message = PoseStamped()
    message.header.frame_id = frames.LAST_SEEN_OUTPUT_FRAME
    if hasattr(message.header, "stamp"):
        seconds = max(0.0, float(candidate.stamp_s))
        message.header.stamp.sec = int(seconds)
        message.header.stamp.nanosec = int((seconds - int(seconds)) * 1_000_000_000)
    message.pose.position.x = candidate.center_xyz[0]
    message.pose.position.y = candidate.center_xyz[1]
    message.pose.position.z = candidate.center_xyz[2]
    message.pose.orientation.x = candidate.orientation_xyzw[0]
    message.pose.orientation.y = candidate.orientation_xyzw[1]
    message.pose.orientation.z = candidate.orientation_xyzw[2]
    message.pose.orientation.w = candidate.orientation_xyzw[3]
    return message
