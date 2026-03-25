from src.go2_cube_perception.go2_cube_perception.depth_roi import BoundingBox2D
from src.go2_cube_perception.go2_cube_perception.object_detector_trt_node import (
    Detector2DCandidate,
    evaluate_detector_runtime_snapshot,
    select_best_candidate,
)


def test_best_candidate_selection_keeps_only_highest_detection_above_threshold() -> None:
    low = Detector2DCandidate(bbox=BoundingBox2D(0, 0, 4, 4), confidence=0.38, stamp_s=1.0)
    mid = Detector2DCandidate(bbox=BoundingBox2D(0, 0, 4, 4), confidence=0.51, stamp_s=1.0)
    high = Detector2DCandidate(bbox=BoundingBox2D(0, 0, 4, 4), confidence=0.83, stamp_s=1.0)

    best = select_best_candidate([low, mid, high], confidence_threshold=0.39)

    assert best == high


def test_detector_runtime_snapshot_requires_fresh_best_candidate_for_visibility() -> None:
    stale = Detector2DCandidate(bbox=BoundingBox2D(0, 0, 4, 4), confidence=0.9, stamp_s=1.0)
    snapshot = evaluate_detector_runtime_snapshot(
        now_s=2.0,
        candidate=stale,
        rgb_stamp_s=1.9,
        camera_info_stamp_s=1.9,
        freshness_timeout_s=0.5,
        rgb_required=False,
        camera_info_required=False,
        rgb_topic="/camera/realsense2_camera/color/image_raw",
        camera_info_topic="/camera/realsense2_camera/color/camera_info",
        internal_candidate_topic="/perception/internal/cube_bbox",
        object_visible_topic="/perception/object_visible",
        look_outputs_enabled=False,
    )

    assert snapshot.candidate_ready is False
