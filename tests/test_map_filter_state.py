from src.go2_object_tracking.go2_object_tracking.map_filter import (
    MapTrackingMeasurement,
    advance_map_filter,
    new_map_tracking_state,
)


def test_map_filter_tracks_position_velocity_and_probability_from_repeated_measurements() -> None:
    state = new_map_tracking_state()
    state = advance_map_filter(
        state,
        now_s=1.0,
        measurement=MapTrackingMeasurement(
            frame_id="map",
            position_xyz=(1.0, 0.0, 0.5),
            confidence=0.8,
            stamp_s=1.0,
            source_frame="camera_link",
        ),
        min_update_confidence=0.39,
    )
    state = advance_map_filter(
        state,
        now_s=2.0,
        measurement=MapTrackingMeasurement(
            frame_id="map",
            position_xyz=(1.5, 0.0, 0.5),
            confidence=0.85,
            stamp_s=2.0,
            source_frame="camera_link",
        ),
        min_update_confidence=0.39,
    )

    assert state.ever_had_fix is True
    assert state.frame_id == "map"
    assert state.position_xyz[0] > 1.0
    assert state.velocity_xyz[0] > 0.0
    assert 0.0 <= state.probability <= 1.0


def test_map_filter_probability_decays_without_new_measurements() -> None:
    state = advance_map_filter(
        new_map_tracking_state(),
        now_s=1.0,
        measurement=MapTrackingMeasurement(
            frame_id="map",
            position_xyz=(0.0, 0.0, 0.0),
            confidence=0.9,
            stamp_s=1.0,
            source_frame="camera_link",
        ),
        min_update_confidence=0.39,
    )
    decayed = advance_map_filter(
        state,
        now_s=3.0,
        measurement=None,
        min_update_confidence=0.39,
    )

    assert decayed.probability < state.probability
