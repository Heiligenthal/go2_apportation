from src.go2_cube_perception.go2_cube_perception.depth_roi import (
    BoundingBox2D,
    CameraIntrinsics,
    PointCloudExtractionConfig,
    extract_local_point_cloud,
)


def test_precise_point_cloud_extracts_local_3d_support_from_roi_depth_and_intrinsics() -> None:
    depth_image = [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ]
    cloud = extract_local_point_cloud(
        depth_image,
        bbox=BoundingBox2D(1, 1, 4, 4),
        intrinsics=CameraIntrinsics(fx=100.0, fy=100.0, cx=2.0, cy=2.0),
        config=PointCloudExtractionConfig(
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=6,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.2,
        ),
    )

    assert cloud is not None
    assert cloud.valid_point_count == 9
    assert abs(cloud.median_depth_m - 1.0) < 1e-6


def test_precise_point_cloud_rejects_too_few_or_spatially_implausible_points() -> None:
    too_sparse = extract_local_point_cloud(
        [[0.0, 0.0], [0.0, 1.0]],
        bbox=BoundingBox2D(0, 0, 2, 2),
        intrinsics=CameraIntrinsics(fx=1.0, fy=1.0, cx=0.0, cy=0.0),
        config=PointCloudExtractionConfig(
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=2,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.1,
        ),
    )
    implausible_extent = extract_local_point_cloud(
        [
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
        ],
        bbox=BoundingBox2D(0, 0, 3, 3),
        intrinsics=CameraIntrinsics(fx=1.0, fy=1.0, cx=0.0, cy=0.0),
        config=PointCloudExtractionConfig(
            min_depth_m=0.4,
            max_depth_m=2.0,
            min_valid_points=4,
            max_depth_deviation_m=0.02,
            max_axis_aligned_extent_m=0.05,
        ),
    )

    assert too_sparse is None
    assert implausible_extent is None
