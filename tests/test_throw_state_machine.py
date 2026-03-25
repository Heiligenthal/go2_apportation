from src.go2_object_tracking.go2_object_tracking.contracts import (
    THROW_STATUS_HELD,
    THROW_STATUS_IDLE,
    THROW_STATUS_LANDED,
    THROW_STATUS_LOST,
    THROW_STATUS_RELEASE_SUSPECTED,
    THROW_STATUS_THROWN,
)
from src.go2_object_tracking.go2_object_tracking.throw_logic import (
    ThrowLogicState,
    ThrowStateMachine,
)


def test_throw_state_machine_only_uses_public_ready_statuses() -> None:
    assert {
        THROW_STATUS_IDLE,
        THROW_STATUS_HELD,
        THROW_STATUS_RELEASE_SUSPECTED,
        THROW_STATUS_THROWN,
        THROW_STATUS_LANDED,
        THROW_STATUS_LOST,
    } == {"IDLE", "HELD", "RELEASE_SUSPECTED", "THROWN", "LANDED", "LOST"}


def test_throw_state_machine_confirms_throw_after_multiple_fast_measurements() -> None:
    machine = ThrowStateMachine(release_speed_threshold_mps=1.0, confirm_measurements=3)
    state = ThrowLogicState()
    state = machine.step(state, object_visible=True, speed_mps=1.2)
    state = machine.step(state, object_visible=True, speed_mps=1.2)
    state = machine.step(state, object_visible=True, speed_mps=1.2)
    assert state.status == "THROWN"


def test_throw_state_machine_marks_lost_when_object_disappears() -> None:
    machine = ThrowStateMachine(release_speed_threshold_mps=1.0, confirm_measurements=2)
    state = machine.step(ThrowLogicState(), object_visible=False, speed_mps=0.0)
    assert state.status == "LOST"
