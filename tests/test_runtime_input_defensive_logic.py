from src.go2_cube_perception.go2_cube_perception.object_detector_trt_node import (
    evaluate_detector_runtime_snapshot,
)
from src.go2_cube_perception.go2_cube_perception.object_position_fast_node import (
    evaluate_fast_runtime_snapshot,
)
from src.go2_cube_perception.go2_cube_perception.object_pose_precise_node import (
    evaluate_precise_runtime_snapshot,
)


def test_detector_runtime_snapshot_blocks_when_required_inputs_are_missing() -> None:
    snapshot = evaluate_detector_runtime_snapshot(
        now_s=5.0,
        candidate=None,
        rgb_stamp_s=None,
        camera_info_stamp_s=None,
        freshness_timeout_s=0.5,
        rgb_required=True,
        camera_info_required=True,
        rgb_topic="/camera/realsense2_camera/color/image_raw",
        camera_info_topic="/camera/realsense2_camera/color/camera_info",
        internal_candidate_topic="/perception/internal/cube_bbox",
        object_visible_topic="/perception/object_visible",
        look_outputs_enabled=False,
    )

    assert snapshot.rgb_ready is False
    assert snapshot.camera_info_ready is False
    assert snapshot.can_publish_visible is False


def test_fast_and_precise_runtime_snapshots_require_fresh_depth_and_intrinsics() -> None:
    fast_snapshot = evaluate_fast_runtime_snapshot(
        now_s=5.0,
        candidate_stamp_s=4.9,
        depth_stamp_s=None,
        intrinsics_stamp_s=4.9,
        freshness_timeout_s=0.2,
        candidate_topic="/perception/internal/cube_bbox",
        depth_topic="/camera/realsense2_camera/aligned_depth_to_color/image_raw",
        camera_info_topic="/camera/realsense2_camera/color/camera_info",
        map_tf_ready=False,
    )
    precise_snapshot = evaluate_precise_runtime_snapshot(
        now_s=5.0,
        candidate_stamp_s=4.9,
        depth_stamp_s=4.0,
        intrinsics_stamp_s=None,
        freshness_timeout_s=0.2,
        candidate_topic="/perception/internal/cube_pose_candidate",
        depth_topic="/camera/realsense2_camera/aligned_depth_to_color/image_raw",
        camera_info_topic="/camera/realsense2_camera/color/camera_info",
        rgb_topic="/camera/realsense2_camera/color/image_raw",
    )

    assert fast_snapshot.can_project is False
    assert fast_snapshot.depth_ready is False
    assert precise_snapshot.can_estimate_pose is False
    assert precise_snapshot.depth_ready is False
    assert precise_snapshot.intrinsics_ready is False
