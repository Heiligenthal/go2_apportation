from src.go2_cube_perception.go2_cube_perception.cube_grasp_pose import (
    build_canonical_cube_grasp_pose,
    canonicalize_axis_mod_pi,
    estimate_cube_grasp_pose,
    CubeGraspEstimatorConfig,
)


def test_axis_canonicalization_treats_pi_flip_as_same_axis() -> None:
    assert canonicalize_axis_mod_pi((1.0, 0.0, 0.0)) == canonicalize_axis_mod_pi((-1.0, 0.0, 0.0))


def test_cube_grasp_pose_keeps_normal_and_mod_pi_edge_axis() -> None:
    pose = build_canonical_cube_grasp_pose(
        center_xyz=(0.1, 0.2, 0.3),
        face_normal=(0.0, 0.0, 1.0),
        edge_axis_mod_pi=(-1.0, 0.0, 0.0),
        source_frame="odom",
    )
    assert pose.face_normal == (0.0, 0.0, 1.0)
    assert pose.edge_axis_mod_pi == (1.0, 0.0, 0.0)
    assert pose.source_frame == "odom"


def test_cube_grasp_estimator_treats_pi_flipped_edge_support_as_same_grasp_axis() -> None:
    points_a = []
    points_b = []
    for x in (-0.02, 0.0, 0.02):
        for y in (-0.02, 0.0, 0.02):
            points_a.append((x, y, 1.0))
            points_b.append((-x, y, 1.0))

    estimate_a = estimate_cube_grasp_pose(
        points_a,
        source_frame="odom",
        config=CubeGraspEstimatorConfig(cube_edge_length_m=0.05, min_valid_points=6),
    )
    estimate_b = estimate_cube_grasp_pose(
        points_b,
        source_frame="odom",
        config=CubeGraspEstimatorConfig(cube_edge_length_m=0.05, min_valid_points=6),
    )

    assert estimate_a is not None
    assert estimate_b is not None
    assert estimate_a.grasp_pose.edge_axis_mod_pi == estimate_b.grasp_pose.edge_axis_mod_pi
