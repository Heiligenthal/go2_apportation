from src.go2_cube_perception.go2_cube_perception.depth_roi import (
    BoundingBox2D,
    DepthRoiConfig,
    summarize_depth_bbox,
)


def test_depth_roi_uses_center_weighted_trimmed_median() -> None:
    depth_image = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.5, 1.5, 1.5, 4.8, 0.0],
        [0.0, 1.5, 1.5, 1.5, 4.7, 0.0],
        [0.0, 1.5, 1.5, 1.5, 4.9, 0.0],
        [0.0, 4.6, 4.7, 4.8, 4.9, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    ]
    summary = summarize_depth_bbox(
        depth_image,
        bbox=BoundingBox2D(1, 1, 5, 5),
        config=DepthRoiConfig(
            min_depth_m=0.4,
            max_depth_m=5.0,
            min_valid_pixels=8,
            trim_ratio=0.1,
            center_weight_multiplier=3,
        ),
    )

    assert summary is not None
    assert abs(summary.depth_m - 1.5) < 1e-6
    assert summary.valid_pixel_count == 16
    assert summary.statistic == "center_weighted_trimmed_median"


def test_depth_roi_rejects_when_too_few_valid_pixels_exist() -> None:
    depth_image = [
        [0.0, 0.0, 0.0],
        [0.0, 1.2, 0.0],
        [0.0, 0.0, 0.0],
    ]

    summary = summarize_depth_bbox(
        depth_image,
        bbox=BoundingBox2D(0, 0, 3, 3),
        config=DepthRoiConfig(
            min_depth_m=0.4,
            max_depth_m=5.0,
            min_valid_pixels=2,
            trim_ratio=0.1,
        ),
    )

    assert summary is None
