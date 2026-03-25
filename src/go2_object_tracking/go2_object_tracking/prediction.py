"""Prediction-region and reacquire gating skeleton."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PredictionGate:
    """Simple confidence/radius gate."""

    radius_m: float
    confidence: float
    valid_for_s: float


def compute_prediction_gate(speed_mps: float, occlusion_s: float, max_radius_m: float) -> PredictionGate:
    """Grow a reacquire gate with speed and occlusion duration."""

    unclamped_radius = speed_mps * max(occlusion_s, 0.0)
    radius_m = min(max_radius_m, unclamped_radius)
    confidence = math.exp(-max(occlusion_s, 0.0))
    return PredictionGate(radius_m=radius_m, confidence=confidence, valid_for_s=max(0.0, occlusion_s))


def should_reacquire(gate: PredictionGate, measured_distance_m: float) -> bool:
    """Decide whether a new measurement fits inside the prediction gate."""

    return measured_distance_m <= gate.radius_m and gate.confidence > 0.0
