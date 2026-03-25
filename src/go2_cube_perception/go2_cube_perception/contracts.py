"""Thin owner-local convenience contracts for cube perception."""

from dataclasses import dataclass
from typing import Tuple

from . import frames, topics
from .backend_types import BackendKind


@dataclass(frozen=True)
class CubePerceptionContracts:
    """Document-/freeze-derived owner mirror without introducing new shared truth."""

    cube_edge_length_m: float = 0.05
    gpu_first_required: bool = True
    color_search_enabled: bool = False
    marker_usage_enabled: bool = False
    active_object_count: int = 1
    best_detection_confidence_threshold: float = 0.39
    fast_output_frame: str = frames.FAST_OUTPUT_FRAME
    precise_output_frame: str = frames.PRECISE_OUTPUT_FRAME
    last_seen_output_frame: str = frames.LAST_SEEN_OUTPUT_FRAME
    internal_tracking_frame: str = frames.INTERNAL_TRACKING_FRAME
    object_visible_topic: str = topics.OBJECT_VISIBLE
    object_pose_topic: str = topics.OBJECT_POSE_6D
    object_last_seen_topic: str = topics.OBJECT_LAST_SEEN
    detections3d_fast_topic: str = topics.DETECTIONS3D_FAST
    internal_map_measurement_topic: str = topics.INTERNAL_MAP_MEASUREMENT
    object_visible_wire_type: str = topics.PUBLIC_WIRE_TYPES[topics.OBJECT_VISIBLE]
    object_pose_wire_type: str = topics.PUBLIC_WIRE_TYPES[topics.OBJECT_POSE_6D]
    object_last_seen_wire_type: str = topics.PUBLIC_WIRE_TYPES[topics.OBJECT_LAST_SEEN]
    detections3d_fast_wire_type: str = topics.PUBLIC_WIRE_TYPES[topics.DETECTIONS3D_FAST]
    default_detector_backend: BackendKind = BackendKind.TENSORRT_STUB
    default_fast_backend: BackendKind = BackendKind.BBOX_DEPTH_STUB
    default_precise_backend: BackendKind = BackendKind.SEGMENTATION_DEPTH_STUB
    blocked_by_h06_topics: Tuple[str, ...] = topics.BLOCKED_BY_H06_OUTPUT_TOPICS


DEFAULT_CONTRACTS = CubePerceptionContracts()
