"""Owner-local camera-based look control helpers for the Bridge handoff."""

from dataclasses import dataclass
from typing import Tuple


LOOK_MODE_OBSERVE_FAST = "OBSERVE_FAST"
LOOK_MODE_INTERCEPT_FAST = "INTERCEPT_FAST"


@dataclass(frozen=True)
class LookControllerConfig:
    """Small P + deadband + rate-limit look controller configuration."""

    yaw_kp: float
    pitch_kp: float
    deadband_norm: float
    yaw_rate_limit_rps: float
    pitch_rate_limit_rps: float
    centered_half_extent_norm: float = 0.125
    centered_dwell_s: float = 0.6
    reposition_no_improvement_s: float = 0.8
    improvement_epsilon: float = 0.02
    edge_proximity_threshold_norm: float = 0.35


@dataclass(frozen=True)
class LookControllerState:
    """Owner-local look-control state for robust centering decisions."""

    last_command_time_s: float = 0.0
    last_yaw_cmd: float = 0.0
    last_pitch_cmd: float = 0.0
    off_center_since_s: float = 0.0
    best_error_norm_since_s: float = 1.0
    improvement_window_started_s: float = 0.0


@dataclass(frozen=True)
class LookControlOutput:
    """Bridge-facing look command proposal without any motion ownership."""

    centered: bool
    yaw_delta: float
    pitch_cmd: float
    balance_rpy: Tuple[float, float, float]
    reposition_needed: bool


def compute_normalized_bbox_error(
    *,
    bbox_center_uv: Tuple[float, float],
    image_size_wh: Tuple[int, int],
) -> Tuple[float, float]:
    """Compute normalized image-plane error from bbox center to image center."""

    width = max(1, int(image_size_wh[0]))
    height = max(1, int(image_size_wh[1]))
    center_u = 0.5 * float(width)
    center_v = 0.5 * float(height)
    ex = (float(bbox_center_uv[0]) - center_u) / float(width)
    ey = (float(bbox_center_uv[1]) - center_v) / float(height)
    return ex, ey


def is_centered(*, ex: float, ey: float, half_extent_norm: float = 0.125) -> bool:
    """Return whether the target center lies inside the 1/4-image rectangle."""

    return abs(float(ex)) <= float(half_extent_norm) and abs(float(ey)) <= float(half_extent_norm)


def _rate_limit(previous_value: float, requested_value: float, dt_s: float, limit_per_s: float) -> float:
    """Clamp control change rate to keep owner-local outputs conservative."""

    if dt_s <= 0.0:
        return float(requested_value)
    max_delta = max(0.0, float(limit_per_s)) * float(dt_s)
    lower = float(previous_value) - max_delta
    upper = float(previous_value) + max_delta
    return max(lower, min(upper, float(requested_value)))


def step_look_controller(
    previous_state: LookControllerState,
    *,
    now_s: float,
    ex: float,
    ey: float,
    mode: str,
    config: LookControllerConfig,
) -> Tuple[LookControllerState, LookControlOutput]:
    """Advance the conservative look controller for OBSERVE/INTERCEPT use."""

    centered = is_centered(ex=ex, ey=ey, half_extent_norm=config.centered_half_extent_norm)
    deadband_ex = 0.0 if abs(ex) <= config.deadband_norm else float(ex)
    deadband_ey = 0.0 if abs(ey) <= config.deadband_norm else float(ey)
    requested_yaw = -config.yaw_kp * deadband_ex
    requested_pitch = -config.pitch_kp * deadband_ey
    dt_s = max(0.0, float(now_s) - float(previous_state.last_command_time_s))
    yaw_delta = _rate_limit(previous_state.last_yaw_cmd, requested_yaw, dt_s, config.yaw_rate_limit_rps)
    pitch_cmd = _rate_limit(previous_state.last_pitch_cmd, requested_pitch, dt_s, config.pitch_rate_limit_rps)
    error_norm = max(abs(float(ex)), abs(float(ey)))

    if centered:
        off_center_since_s = 0.0
        best_error_norm_since_s = error_norm
        improvement_window_started_s = float(now_s)
        reposition_needed = False
    else:
        off_center_since_s = (
            float(previous_state.off_center_since_s)
            if float(previous_state.off_center_since_s) > 0.0
            else float(now_s)
        )
        improvement_window_started_s = (
            float(previous_state.improvement_window_started_s)
            if float(previous_state.improvement_window_started_s) > 0.0
            else float(now_s)
        )
        best_error_norm_since_s = min(float(previous_state.best_error_norm_since_s), error_norm)
        long_off_center = (
            float(now_s) - float(off_center_since_s)
        ) >= config.centered_dwell_s
        near_edge = abs(float(ex)) >= config.edge_proximity_threshold_norm or abs(float(ey)) >= config.edge_proximity_threshold_norm
        no_improvement = (
            float(now_s) - float(improvement_window_started_s)
        ) >= config.reposition_no_improvement_s and (
            error_norm <= float(best_error_norm_since_s) + config.improvement_epsilon
        )
        reposition_needed = bool(long_off_center and near_edge and no_improvement)

    next_state = LookControllerState(
        last_command_time_s=float(now_s),
        last_yaw_cmd=float(yaw_delta),
        last_pitch_cmd=float(pitch_cmd),
        off_center_since_s=float(off_center_since_s),
        best_error_norm_since_s=float(best_error_norm_since_s),
        improvement_window_started_s=float(improvement_window_started_s),
    )
    output = LookControlOutput(
        centered=centered,
        yaw_delta=float(yaw_delta),
        pitch_cmd=float(pitch_cmd),
        balance_rpy=(0.0, float(pitch_cmd), float(yaw_delta) if mode == LOOK_MODE_OBSERVE_FAST else 0.0),
        reposition_needed=reposition_needed,
    )
    return next_state, output
