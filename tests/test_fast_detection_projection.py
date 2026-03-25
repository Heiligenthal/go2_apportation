from src.go2_cube_perception.go2_cube_perception.depth_roi import BoundingBox2D, CameraIntrinsics
from src.go2_cube_perception.go2_cube_perception.object_detector_trt_node import Detector2DCandidate
from src.go2_cube_perception.go2_cube_perception.object_position_fast_node import (
    FastProjectionConfig,
    build_public_fast_detection,
)


def test_fast_projection_builds_public_detection_candidate_from_bbox_depth_and_intrinsics() -> None:
    depth_image = [
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 2.0, 2.0, 0.0],
        [0.0, 2.0, 2.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ]
    candidate = Detector2DCandidate(
        bbox=BoundingBox2D(1, 1, 3, 3),
        confidence=0.82,
        frame_id="odom",
        stamp_s=12.5,
        source_hint="unit_test",
    )

    detection = build_public_fast_detection(
        candidate,
        depth_image=depth_image,
        intrinsics=CameraIntrinsics(fx=2.0, fy=2.0, cx=0.0, cy=0.0),
        config=FastProjectionConfig(
            output_frame="odom",
            min_depth_m=0.4,
            max_depth_m=5.0,
            min_valid_pixels=4,
            trim_ratio=0.1,
        ),
    )

    assert detection is not None
    assert detection.frame_id == "odom"
    assert detection.center_xyz == (2.0, 2.0, 2.0)
    assert detection.confidence == 0.82
    assert detection.stamp_s == 12.5


def test_fast_projection_drops_candidate_when_frame_handoff_is_unsafe() -> None:
    depth_image = [
        [1.0, 1.0],
        [1.0, 1.0],
    ]
    candidate = Detector2DCandidate(
        bbox=BoundingBox2D(0, 0, 2, 2),
        confidence=0.9,
        frame_id="camera_link",
    )

    detection = build_public_fast_detection(
        candidate,
        depth_image=depth_image,
        intrinsics=CameraIntrinsics(fx=1.0, fy=1.0, cx=0.0, cy=0.0),
        config=FastProjectionConfig(
            output_frame="odom",
            min_depth_m=0.4,
            max_depth_m=5.0,
            min_valid_pixels=4,
            trim_ratio=0.1,
            allow_frame_passthrough_if_no_tf=False,
        ),
    )

    assert detection is None


def test_fast_projection_drops_candidate_with_insufficient_depth_support() -> None:
    depth_image = [
        [0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0],
    ]
    candidate = Detector2DCandidate(
        bbox=BoundingBox2D(0, 0, 3, 3),
        confidence=0.7,
        frame_id="odom",
    )

    detection = build_public_fast_detection(
        candidate,
        depth_image=depth_image,
        intrinsics=CameraIntrinsics(fx=1.0, fy=1.0, cx=1.0, cy=1.0),
        config=FastProjectionConfig(
            output_frame="odom",
            min_depth_m=0.4,
            max_depth_m=5.0,
            min_valid_pixels=2,
            trim_ratio=0.1,
        ),
    )

    assert detection is None
