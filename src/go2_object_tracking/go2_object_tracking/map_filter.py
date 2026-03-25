"""Owner-local map-frame tracking filter for cube estimates."""

from dataclasses import dataclass
import math
from typing import Optional, Tuple


Vector3Tuple = Tuple[float, float, float]
Matrix3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]


@dataclass(frozen=True)
class MapTrackingMeasurement:
    """Owner-local map-frame measurement for the cube filter."""

    frame_id: str
    position_xyz: Vector3Tuple
    confidence: float
    stamp_s: float
    source_frame: str
    bbox_center_norm_xy: Tuple[float, float] = (0.0, 0.0)
    centered: bool = False


@dataclass(frozen=True)
class AxisKalmanState:
    """Single-axis constant-acceleration filter state."""

    x: Tuple[float, float, float]
    p: Matrix3


@dataclass(frozen=True)
class MapTrackingState:
    """Owner-local map-based tracking state."""

    frame_id: str
    position_xyz: Vector3Tuple
    velocity_xyz: Vector3Tuple
    acceleration_xyz: Vector3Tuple
    probability: float
    stamp_s: float
    covariance_diag: Vector3Tuple
    source_frame: str
    bbox_center_norm_xy: Tuple[float, float]
    centered: bool
    ever_had_fix: bool
    axis_states: Tuple[AxisKalmanState, AxisKalmanState, AxisKalmanState]


def _identity_covariance(scale: float) -> Matrix3:
    return (
        (float(scale), 0.0, 0.0),
        (0.0, float(scale), 0.0),
        (0.0, 0.0, float(scale)),
    )


def new_map_tracking_state(frame_id: str = "map") -> MapTrackingState:
    """Build an empty owner-local map filter state."""

    axis = AxisKalmanState(x=(0.0, 0.0, 0.0), p=_identity_covariance(1.0))
    return MapTrackingState(
        frame_id=frame_id,
        position_xyz=(0.0, 0.0, 0.0),
        velocity_xyz=(0.0, 0.0, 0.0),
        acceleration_xyz=(0.0, 0.0, 0.0),
        probability=0.0,
        stamp_s=0.0,
        covariance_diag=(1.0, 1.0, 1.0),
        source_frame="",
        bbox_center_norm_xy=(0.0, 0.0),
        centered=False,
        ever_had_fix=False,
        axis_states=(axis, axis, axis),
    )


def _matmul(a: Matrix3, b: Matrix3) -> Matrix3:
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3))
        for row in range(3)
    )


def _transpose(m: Matrix3) -> Matrix3:
    return tuple(tuple(m[col][row] for col in range(3)) for row in range(3))


def _matvec(m: Matrix3, x: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return tuple(sum(m[row][col] * x[col] for col in range(3)) for row in range(3))


def _matadd(a: Matrix3, b: Matrix3) -> Matrix3:
    return tuple(
        tuple(a[row][col] + b[row][col] for col in range(3)) for row in range(3)
    )


def _predict_axis(axis: AxisKalmanState, dt_s: float, process_noise: float) -> AxisKalmanState:
    dt = max(0.0, float(dt_s))
    f = (
        (1.0, dt, 0.5 * dt * dt),
        (0.0, 1.0, dt),
        (0.0, 0.0, 1.0),
    )
    q_scale = max(1e-6, float(process_noise))
    q = (
        (q_scale * dt ** 4, 0.0, 0.0),
        (0.0, q_scale * dt ** 2, 0.0),
        (0.0, 0.0, q_scale),
    )
    predicted_x = _matvec(f, axis.x)
    predicted_p = _matadd(_matmul(_matmul(f, axis.p), _transpose(f)), q)
    return AxisKalmanState(x=predicted_x, p=predicted_p)


def _update_axis(
    axis: AxisKalmanState,
    *,
    measurement: float,
    measurement_variance: float,
) -> AxisKalmanState:
    h = (1.0, 0.0, 0.0)
    innovation = float(measurement) - float(axis.x[0])
    s = (
        axis.p[0][0] * h[0]
        + axis.p[0][1] * h[1]
        + axis.p[0][2] * h[2]
        + float(measurement_variance)
    )
    if s <= 1e-9:
        return axis
    k = (
        axis.p[0][0] / s,
        axis.p[1][0] / s,
        axis.p[2][0] / s,
    )
    updated_x = tuple(axis.x[i] + k[i] * innovation for i in range(3))
    kh = (
        (k[0] * h[0], k[0] * h[1], k[0] * h[2]),
        (k[1] * h[0], k[1] * h[1], k[1] * h[2]),
        (k[2] * h[0], k[2] * h[1], k[2] * h[2]),
    )
    identity = _identity_covariance(1.0)
    i_minus_kh = tuple(
        tuple(identity[row][col] - kh[row][col] for col in range(3)) for row in range(3)
    )
    updated_p = _matmul(i_minus_kh, axis.p)
    return AxisKalmanState(x=updated_x, p=updated_p)


def advance_map_filter(
    previous_state: MapTrackingState,
    *,
    now_s: float,
    measurement: Optional[MapTrackingMeasurement],
    min_update_confidence: float,
    process_noise: float = 0.12,
    measurement_noise_base: float = 0.04,
    probability_decay_per_s: float = 0.45,
) -> MapTrackingState:
    """Advance the owner-local map filter with optional measurement update."""

    current_state = previous_state
    if not previous_state.ever_had_fix and measurement is None:
        return previous_state
    if not previous_state.ever_had_fix and measurement is not None and measurement.confidence >= min_update_confidence:
        variance = max(1e-4, float(measurement_noise_base) / max(float(measurement.confidence), 1e-3))
        axis_states = tuple(
            AxisKalmanState(x=(float(value), 0.0, 0.0), p=_identity_covariance(variance))
            for value in measurement.position_xyz
        )
        return MapTrackingState(
            frame_id=measurement.frame_id,
            position_xyz=tuple(float(value) for value in measurement.position_xyz),
            velocity_xyz=(0.0, 0.0, 0.0),
            acceleration_xyz=(0.0, 0.0, 0.0),
            probability=max(0.0, min(1.0, float(measurement.confidence))),
            stamp_s=float(now_s),
            covariance_diag=(variance, variance, variance),
            source_frame=measurement.source_frame,
            bbox_center_norm_xy=measurement.bbox_center_norm_xy,
            centered=bool(measurement.centered),
            ever_had_fix=True,
            axis_states=axis_states,  # type: ignore[arg-type]
        )

    dt_s = max(0.0, float(now_s) - float(previous_state.stamp_s))
    predicted_axes = tuple(_predict_axis(axis, dt_s, process_noise) for axis in previous_state.axis_states)
    probability = max(0.0, min(1.0, float(previous_state.probability) * math.exp(-probability_decay_per_s * dt_s)))
    source_frame = previous_state.source_frame
    bbox_center_norm_xy = previous_state.bbox_center_norm_xy
    centered = previous_state.centered

    if measurement is not None and measurement.confidence >= min_update_confidence:
        measurement_variance = max(
            1e-4,
            float(measurement_noise_base) / max(float(measurement.confidence), 1e-3),
        )
        predicted_axes = tuple(
            _update_axis(
                predicted_axes[index],
                measurement=float(measurement.position_xyz[index]),
                measurement_variance=measurement_variance,
            )
            for index in range(3)
        )
        probability = max(probability, min(1.0, float(measurement.confidence)))
        source_frame = measurement.source_frame
        bbox_center_norm_xy = measurement.bbox_center_norm_xy
        centered = bool(measurement.centered)

    position_xyz = tuple(float(axis.x[0]) for axis in predicted_axes)
    velocity_xyz = tuple(float(axis.x[1]) for axis in predicted_axes)
    acceleration_xyz = tuple(float(axis.x[2]) for axis in predicted_axes)
    covariance_diag = tuple(float(axis.p[0][0]) for axis in predicted_axes)
    return MapTrackingState(
        frame_id=previous_state.frame_id,
        position_xyz=position_xyz,
        velocity_xyz=velocity_xyz,
        acceleration_xyz=acceleration_xyz,
        probability=probability,
        stamp_s=float(now_s),
        covariance_diag=covariance_diag,  # type: ignore[arg-type]
        source_frame=source_frame,
        bbox_center_norm_xy=bbox_center_norm_xy,
        centered=centered,
        ever_had_fix=True,
        axis_states=predicted_axes,  # type: ignore[arg-type]
    )
