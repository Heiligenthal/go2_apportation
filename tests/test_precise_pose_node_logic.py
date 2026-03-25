from src.go2_cube_perception.go2_cube_perception.depth_roi import BoundingBox2D, CameraIntrinsics
from src.go2_cube_perception.go2_cube_perception.object_pose_precise_node import (
    PrecisePoseComputationConfig,
    PreciseRoiCandidate,
    RigidTransform,
    decide_precise_publication,
    estimate_precise_pose_from_candidate,
    resolve_last_seen_candidate,
)
from src.go2_cube_perception.go2_cube_perception.msg_adapters import InternalPrecisePoseCandidate


def test_precise_pose_is_built_only_when_geometry_is_plausible() -> None:
    depth_image = [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ]
    estimate = estimate_precise_pose_from_candidate(
        PreciseRoiCandidate(
            bbox=BoundingBox2D(1, 1, 4, 4),
            confidence=0.88,
            frame_id="odom",
            stamp_s=5.0,
        ),
        depth_image=depth_image,
        intrinsics=CameraIntrinsics(fx=100.0, fy=100.0, cx=2.0, cy=2.0),
        config=PrecisePoseComputationConfig(
            output_pose_frame="odom",
            last_seen_frame="map",
            cube_edge_length_m=0.05,
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=6,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.1,
            min_in_plane_span_m=0.01,
            max_in_plane_span_m=0.09,
            max_face_thickness_m=0.01,
        ),
    )

    assert estimate is not None
    assert estimate.grasp_pose.source_frame == "odom"


def test_precise_pose_is_rejected_when_output_frame_handoff_is_not_safe() -> None:
    estimate = estimate_precise_pose_from_candidate(
        PreciseRoiCandidate(
            bbox=BoundingBox2D(0, 0, 3, 3),
            confidence=0.8,
            frame_id="camera_link",
        ),
        depth_image=[
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
        ],
        intrinsics=CameraIntrinsics(fx=100.0, fy=100.0, cx=1.0, cy=1.0),
        config=PrecisePoseComputationConfig(
            output_pose_frame="odom",
            last_seen_frame="map",
            cube_edge_length_m=0.05,
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=4,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.2,
            min_in_plane_span_m=0.005,
            max_in_plane_span_m=0.09,
            max_face_thickness_m=0.01,
        ),
    )

    assert estimate is None


def test_precise_last_seen_requires_valid_pose_and_map_frame() -> None:
    depth_image = [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ]
    odom_estimate = estimate_precise_pose_from_candidate(
        PreciseRoiCandidate(
            bbox=BoundingBox2D(1, 1, 4, 4),
            confidence=0.88,
            frame_id="odom",
        ),
        depth_image=depth_image,
        intrinsics=CameraIntrinsics(fx=100.0, fy=100.0, cx=2.0, cy=2.0),
        config=PrecisePoseComputationConfig(
            output_pose_frame="odom",
            last_seen_frame="map",
            cube_edge_length_m=0.05,
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=6,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.1,
            min_in_plane_span_m=0.01,
            max_in_plane_span_m=0.09,
            max_face_thickness_m=0.01,
        ),
    )
    map_estimate = estimate_precise_pose_from_candidate(
        PreciseRoiCandidate(
            bbox=BoundingBox2D(1, 1, 4, 4),
            confidence=0.88,
            frame_id="map",
        ),
        depth_image=depth_image,
        intrinsics=CameraIntrinsics(fx=100.0, fy=100.0, cx=2.0, cy=2.0),
        config=PrecisePoseComputationConfig(
            output_pose_frame="map",
            last_seen_frame="map",
            cube_edge_length_m=0.05,
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=6,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.1,
            min_in_plane_span_m=0.01,
            max_in_plane_span_m=0.09,
            max_face_thickness_m=0.01,
        ),
    )

    assert decide_precise_publication(None, last_seen_frame="map").publish_last_seen is False
    assert odom_estimate is not None
    assert decide_precise_publication(odom_estimate, last_seen_frame="map").publish_last_seen is False
    assert map_estimate is not None
    assert decide_precise_publication(map_estimate, last_seen_frame="map").publish_last_seen is True


def test_precise_last_seen_can_be_resolved_via_transform_provider() -> None:
    candidate = InternalPrecisePoseCandidate(
        frame_id="odom",
        center_xyz=(0.0, 0.0, 1.0),
        face_normal=(0.0, 0.0, 1.0),
        edge_axis_mod_pi=(1.0, 0.0, 0.0),
        confidence=0.9,
        stamp_s=3.0,
    )

    transformed = resolve_last_seen_candidate(
        candidate,
        last_seen_frame="map",
        transform_provider=lambda source_frame, target_frame, stamp_s: (
            None
            if (source_frame, target_frame, stamp_s) != ("odom", "map", 3.0)
            else RigidTransform(
                target_frame="map",
                translation_xyz=(1.0, 2.0, 0.0),
                rotation_xyzw=(0.0, 0.0, 0.0, 1.0),
            )
        ),
    )

    assert transformed is not None
    assert transformed.frame_id == "map"
