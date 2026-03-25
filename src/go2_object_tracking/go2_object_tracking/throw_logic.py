"""Throw-state skeleton for visible/occluded tracking."""

from dataclasses import dataclass

from .contracts import (
    THROW_STATUS_HELD,
    THROW_STATUS_IDLE,
    THROW_STATUS_LANDED,
    THROW_STATUS_LOST,
    THROW_STATUS_RELEASE_SUSPECTED,
    THROW_STATUS_THROWN,
)


@dataclass(frozen=True)
class ThrowLogicState:
    """Small deterministic throw-state snapshot."""

    status: str = THROW_STATUS_IDLE
    release_candidate_count: int = 0


class ThrowStateMachine:
    """Small throw-state machine with no motion side effects."""

    def __init__(self, release_speed_threshold_mps: float, confirm_measurements: int) -> None:
        self.release_speed_threshold_mps = release_speed_threshold_mps
        self.confirm_measurements = confirm_measurements

    def step(
        self,
        state: ThrowLogicState,
        *,
        object_visible: bool,
        speed_mps: float,
        object_landed: bool = False,
    ) -> ThrowLogicState:
        """Advance the throw state with simple, reviewable rules."""

        if object_landed:
            return ThrowLogicState(status=THROW_STATUS_LANDED, release_candidate_count=0)
        if not object_visible:
            return ThrowLogicState(status=THROW_STATUS_LOST, release_candidate_count=0)
        if speed_mps < self.release_speed_threshold_mps:
            return ThrowLogicState(status=THROW_STATUS_HELD, release_candidate_count=0)

        new_count = state.release_candidate_count + 1
        if new_count >= self.confirm_measurements:
            return ThrowLogicState(status=THROW_STATUS_THROWN, release_candidate_count=new_count)
        return ThrowLogicState(status=THROW_STATUS_RELEASE_SUSPECTED, release_candidate_count=new_count)
