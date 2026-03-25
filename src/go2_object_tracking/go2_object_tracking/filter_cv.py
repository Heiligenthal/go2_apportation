"""Constant-velocity filter skeleton."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CvFilterState:
    """Minimal constant-velocity state."""

    position_xyz: Tuple[float, float, float]
    velocity_xyz: Tuple[float, float, float]
    stamp_s: float


def predict_cv(state: CvFilterState, query_time_s: float) -> CvFilterState:
    """Predict with a constant-velocity model."""

    dt = max(0.0, query_time_s - state.stamp_s)
    position = tuple(state.position_xyz[i] + state.velocity_xyz[i] * dt for i in range(3))
    return CvFilterState(position_xyz=position, velocity_xyz=state.velocity_xyz, stamp_s=query_time_s)
