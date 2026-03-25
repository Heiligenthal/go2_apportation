from src.go2_cube_perception.go2_cube_perception.look_control import (
    LOOK_MODE_OBSERVE_FAST,
    LookControllerConfig,
    LookControllerState,
    compute_normalized_bbox_error,
    is_centered,
    step_look_controller,
)


def test_normalized_bbox_error_and_center_window_follow_quarter_image_rule() -> None:
    ex, ey = compute_normalized_bbox_error(bbox_center_uv=(320.0, 240.0), image_size_wh=(640, 480))
    assert ex == 0.0
    assert ey == 0.0
    assert is_centered(ex=0.12, ey=-0.12) is True
    assert is_centered(ex=0.13, ey=0.0) is False


def test_look_controller_rate_limits_and_delays_reposition_request() -> None:
    config = LookControllerConfig(
        yaw_kp=0.8,
        pitch_kp=0.6,
        deadband_norm=0.03,
        yaw_rate_limit_rps=0.2,
        pitch_rate_limit_rps=0.2,
        centered_dwell_s=0.6,
        reposition_no_improvement_s=0.8,
        improvement_epsilon=0.02,
    )
    state = LookControllerState()
    state, early = step_look_controller(
        state,
        now_s=0.2,
        ex=0.4,
        ey=0.2,
        mode=LOOK_MODE_OBSERVE_FAST,
        config=config,
    )
    state, late = step_look_controller(
        state,
        now_s=1.2,
        ex=0.4,
        ey=0.2,
        mode=LOOK_MODE_OBSERVE_FAST,
        config=config,
    )

    assert abs(early.yaw_delta) <= 0.2 * 0.2 + 1e-6
    assert early.reposition_needed is False
    assert late.reposition_needed is True
