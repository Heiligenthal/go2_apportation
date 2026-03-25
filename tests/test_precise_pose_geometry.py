from src.go2_cube_perception.go2_cube_perception.cube_grasp_pose import (
    CubeGraspEstimatorConfig,
    estimate_cube_grasp_pose,
)


def test_precise_grasp_geometry_estimates_center_and_canonical_orientation_for_visible_face() -> None:
    points_xyz = []
    for x in (-0.015, 0.0, 0.015):
        for y in (-0.015, 0.0, 0.015):
            points_xyz.append((x, y, 1.0))

    estimate = estimate_cube_grasp_pose(
        points_xyz,
        source_frame="odom",
        config=CubeGraspEstimatorConfig(
            cube_edge_length_m=0.05,
            min_valid_points=6,
            min_in_plane_span_m=0.01,
            max_in_plane_span_m=0.09,
            max_face_thickness_m=0.01,
        ),
    )

    assert estimate is not None
    assert abs(estimate.grasp_pose.center_xyz[2] - 1.025) < 1e-6
    assert estimate.grasp_pose.source_frame == "odom"
    assert estimate.diagnostics.face_thickness_m <= 0.01


def test_precise_grasp_geometry_rejects_thick_non_face_support() -> None:
    points_xyz = [
        (-0.01, -0.01, 0.96),
        (0.01, -0.01, 0.98),
        (-0.01, 0.01, 1.00),
        (0.01, 0.01, 1.04),
        (0.00, 0.00, 1.08),
        (0.00, 0.01, 1.10),
    ]

    estimate = estimate_cube_grasp_pose(
        points_xyz,
        source_frame="odom",
        config=CubeGraspEstimatorConfig(
            cube_edge_length_m=0.05,
            min_valid_points=6,
            min_in_plane_span_m=0.005,
            max_in_plane_span_m=0.09,
            max_face_thickness_m=0.01,
        ),
    )

    assert estimate is None
