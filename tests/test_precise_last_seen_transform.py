from src.go2_cube_perception.go2_cube_perception.msg_adapters import InternalPrecisePoseCandidate
from src.go2_cube_perception.go2_cube_perception.object_pose_precise_node import (
    RigidTransform,
    resolve_last_seen_candidate,
)


def test_precise_last_seen_does_not_fake_map_without_transform() -> None:
    candidate = InternalPrecisePoseCandidate(
        frame_id="odom",
        center_xyz=(1.0, 2.0, 3.0),
        face_normal=(0.0, 0.0, 1.0),
        edge_axis_mod_pi=(1.0, 0.0, 0.0),
        confidence=0.8,
    )

    assert resolve_last_seen_candidate(candidate, last_seen_frame="map", transform_provider=None) is None


def test_precise_last_seen_uses_trustworthy_transform_when_available() -> None:
    candidate = InternalPrecisePoseCandidate(
        frame_id="odom",
        center_xyz=(1.0, 2.0, 3.0),
        face_normal=(0.0, 0.0, 1.0),
        edge_axis_mod_pi=(1.0, 0.0, 0.0),
        confidence=0.8,
        orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
        stamp_s=7.0,
    )

    def transform_provider(source_frame: str, target_frame: str, stamp_s: float):
        assert source_frame == "odom"
        assert target_frame == "map"
        assert stamp_s == 7.0
        return RigidTransform(
            target_frame="map",
            translation_xyz=(0.5, -0.5, 1.0),
            rotation_xyzw=(0.0, 0.0, 0.0, 1.0),
        )

    transformed = resolve_last_seen_candidate(
        candidate,
        last_seen_frame="map",
        transform_provider=transform_provider,
    )

    assert transformed is not None
    assert transformed.frame_id == "map"
    assert transformed.center_xyz == (1.5, 1.5, 4.0)
