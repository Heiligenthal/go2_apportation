"""Ballistic filter skeleton."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class BallisticFilterState:
    """Minimal ballistic state."""

    position_xyz: Tuple[float, float, float]
    velocity_xyz: Tuple[float, float, float]
    stamp_s: float


def predict_ballistic(
    state: BallisticFilterState,
    query_time_s: float,
    gravity_mps2: float = 9.81,
) -> BallisticFilterState:
    """Predict with a ballistic motion model."""

    dt = max(0.0, query_time_s - state.stamp_s)
    next_position = (
        state.position_xyz[0] + state.velocity_xyz[0] * dt,
        state.position_xyz[1] + state.velocity_xyz[1] * dt,
        state.position_xyz[2] + state.velocity_xyz[2] * dt - 0.5 * gravity_mps2 * dt * dt,
    )
    next_velocity = (
        state.velocity_xyz[0],
        state.velocity_xyz[1],
        state.velocity_xyz[2] - gravity_mps2 * dt,
    )
    return BallisticFilterState(position_xyz=next_position, velocity_xyz=next_velocity, stamp_s=query_time_s)
