from src.go2_object_tracking.go2_object_tracking.prediction import (
    compute_prediction_gate,
    should_reacquire,
)


def test_prediction_gate_grows_with_occlusion_and_stays_bounded() -> None:
    gate = compute_prediction_gate(speed_mps=2.0, occlusion_s=1.0, max_radius_m=1.0)
    assert gate.radius_m == 1.0
    assert 0.0 < gate.confidence < 1.0


def test_prediction_gate_accepts_measurements_inside_radius() -> None:
    gate = compute_prediction_gate(speed_mps=0.5, occlusion_s=0.4, max_radius_m=1.0)
    assert should_reacquire(gate, measured_distance_m=0.1) is True
    assert should_reacquire(gate, measured_distance_m=1.5) is False
