#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import os
import select
import shlex
import shutil
import sys
import termios
import time
import tty
from dataclasses import dataclass
from pathlib import Path

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


ROOT_DIR = Path(__file__).resolve().parents[2]
MANUAL_ROOT = ROOT_DIR / "artifacts" / "manual_calibration"
CAMERA_CALIBRATION_ROOT = ROOT_DIR / "artifacts" / "calibration" / "camera_mount"
LIDAR_CONFIG_ENV = ROOT_DIR / "config" / "mapping_test_extrinsics.env"


@dataclass
class ExtrinsicsState:
    xyz: list[float]
    rpy_deg: list[float]


@dataclass
class StepSize:
    name: str
    translation_m: float
    rotation_deg: float


STEP_SIZES = [
    StepSize("fine", 0.002, 0.2),
    StepSize("medium", 0.005, 0.5),
    StepSize("coarse", 0.01, 1.0),
]


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed = shlex.split(value, comments=False, posix=True)
        values[key.strip()] = parsed[0] if len(parsed) == 1 else " ".join(parsed)
    return values


def latest_camera_calibration_env() -> Path | None:
    latest_link = CAMERA_CALIBRATION_ROOT / "latest"
    if latest_link.is_symlink():
        resolved = (CAMERA_CALIBRATION_ROOT / os.readlink(latest_link)).resolve()
        candidate = resolved / "best_extrinsics.env"
        if candidate.is_file():
            return candidate

    candidates = sorted(
        (
            path / "best_extrinsics.env"
            for path in CAMERA_CALIBRATION_ROOT.glob("*")
            if path.is_dir() and (path / "best_extrinsics.env").is_file()
        ),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_triplet(value: str, *, cast=float) -> list[float]:
    parts = value.split()
    if len(parts) != 3:
        raise ValueError(f"Expected 3 values, got {value!r}")
    return [cast(part) for part in parts]


def latest_manual_calibration_dir() -> Path | None:
    latest_link = MANUAL_ROOT / "latest"
    if latest_link.is_symlink():
        resolved = Path(os.readlink(latest_link))
        if not resolved.is_absolute():
            resolved = (MANUAL_ROOT / resolved).resolve()
        if resolved.is_dir():
            return resolved

    candidates = sorted(
        (path for path in MANUAL_ROOT.glob("*") if path.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def latest_manual_env_candidates() -> list[Path]:
    latest_dir = latest_manual_calibration_dir()
    if latest_dir is None:
        return []
    return [
        latest_dir / "manual_sensor_extrinsics.env",
        latest_dir / "camera_manual_extrinsics.env",
        latest_dir / "lidar_manual_extrinsics.env",
    ]


def load_initial_camera_state(logs: list[str]) -> ExtrinsicsState:
    manual_dir = latest_manual_calibration_dir()
    if manual_dir is not None:
        manual_env = manual_dir / "manual_sensor_extrinsics.env"
        if manual_env.is_file():
            values = parse_env_file(manual_env)
            xyz_value = values.get("CAMERA_XYZ")
            rpy_value = values.get("CAMERA_RPY")
            if xyz_value and rpy_value:
                logs.append(f"camera init: loaded latest manual calibration from {manual_env}")
                return ExtrinsicsState(parse_triplet(xyz_value), parse_triplet(rpy_value))

        camera_env = manual_dir / "camera_manual_extrinsics.env"
        if camera_env.is_file():
            values = parse_env_file(camera_env)
            xyz_value = values.get("CAMERA_XYZ")
            rpy_value = values.get("CAMERA_RPY")
            if xyz_value and rpy_value:
                logs.append(f"camera init: loaded manual camera values from {camera_env}")
                return ExtrinsicsState(parse_triplet(xyz_value), parse_triplet(rpy_value))

    env_path = latest_camera_calibration_env()
    if env_path is None:
        logs.append("camera init: no camera-mount calibration found; starting from zeros")
        return ExtrinsicsState([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    values = parse_env_file(env_path)
    required = ["X", "Y", "Z", "ROLL_DEG", "PITCH_DEG", "YAW_DEG"]
    missing = [key for key in required if key not in values]
    if missing:
        logs.append(
            f"camera init: {env_path} missing {', '.join(missing)}; starting from zeros"
        )
        return ExtrinsicsState([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    xyz = [float(values["X"]), float(values["Y"]), float(values["Z"])]
    rpy_deg = [float(values["ROLL_DEG"]), float(values["PITCH_DEG"]), float(values["YAW_DEG"])]
    logs.append(f"camera init: loaded latest calibration from {env_path}")
    return ExtrinsicsState(xyz, rpy_deg)


def load_initial_lidar_state(default_frame: str, logs: list[str]) -> tuple[str, ExtrinsicsState]:
    manual_dir = latest_manual_calibration_dir()
    if manual_dir is not None:
        manual_env = manual_dir / "manual_sensor_extrinsics.env"
        if manual_env.is_file():
            values = parse_env_file(manual_env)
            lidar_frame = values.get("LIDAR_FRAME", default_frame).strip() or default_frame
            xyz_value = values.get("LIDAR_XYZ")
            rpy_value = values.get("LIDAR_RPY")
            if xyz_value and rpy_value:
                logs.append(f"lidar init: loaded latest manual calibration from {manual_env}")
                return lidar_frame, ExtrinsicsState(parse_triplet(xyz_value), parse_triplet(rpy_value))

        lidar_env = manual_dir / "lidar_manual_extrinsics.env"
        if lidar_env.is_file():
            values = parse_env_file(lidar_env)
            lidar_frame = values.get("LIDAR_FRAME", default_frame).strip() or default_frame
            xyz_value = values.get("LIDAR_XYZ")
            rpy_value = values.get("LIDAR_RPY")
            if xyz_value and rpy_value:
                logs.append(f"lidar init: loaded manual lidar values from {lidar_env}")
                return lidar_frame, ExtrinsicsState(parse_triplet(xyz_value), parse_triplet(rpy_value))

    if not LIDAR_CONFIG_ENV.is_file():
        logs.append("lidar init: no existing LiDAR env found; starting from zeros")
        return default_frame, ExtrinsicsState([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    values = parse_env_file(LIDAR_CONFIG_ENV)
    lidar_frame = values.get("LIDAR_FRAME", default_frame).strip() or default_frame
    xyz_value = values.get("LIDAR_XYZ")
    rpy_value = values.get("LIDAR_RPY")
    if not xyz_value or not rpy_value:
        logs.append(
            f"lidar init: {LIDAR_CONFIG_ENV} missing LIDAR_XYZ/LIDAR_RPY; starting from zeros"
        )
        return lidar_frame, ExtrinsicsState([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    xyz = parse_triplet(xyz_value)
    rpy_deg = parse_triplet(rpy_value)
    logs.append(f"lidar init: loaded existing values from {LIDAR_CONFIG_ENV}")
    return lidar_frame, ExtrinsicsState(xyz, rpy_deg)


def quaternion_from_euler_deg(roll_deg: float, pitch_deg: float, yaw_deg: float) -> tuple[float, float, float, float]:
    roll = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)

    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return qx, qy, qz, qw


class ManualExtrinsicsPublisher(Node):
    def __init__(self, base_frame: str, camera_frame: str, lidar_frame: str) -> None:
        super().__init__("manual_sensor_extrinsics_helper")
        self._base_frame = base_frame
        self._camera_frame = camera_frame
        self._lidar_frame = lidar_frame
        self._tf_broadcaster = TransformBroadcaster(self)

    def publish_state(self, camera_state: ExtrinsicsState, lidar_state: ExtrinsicsState) -> None:
        now = self.get_clock().now().to_msg()
        self._tf_broadcaster.sendTransform(
            [
                self._build_transform(now, self._camera_frame, camera_state),
                self._build_transform(now, self._lidar_frame, lidar_state),
            ]
        )

    def _build_transform(
        self,
        stamp,
        child_frame: str,
        state: ExtrinsicsState,
    ) -> TransformStamped:
        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = self._base_frame
        transform.child_frame_id = child_frame
        transform.transform.translation.x = state.xyz[0]
        transform.transform.translation.y = state.xyz[1]
        transform.transform.translation.z = state.xyz[2]
        qx, qy, qz, qw = quaternion_from_euler_deg(*state.rpy_deg)
        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw
        return transform


class RawTerminal:
    def __enter__(self) -> "RawTerminal":
        self._fd = sys.stdin.fileno()
        self._settings = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._settings)


def write_env_file(path: Path, values: dict[str, str]) -> None:
    lines = [f"{key}={shlex.quote(value)}" for key, value in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_current_values(
    output_dir: Path,
    camera_frame: str,
    lidar_frame: str,
    camera_state: ExtrinsicsState,
    lidar_state: ExtrinsicsState,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    latest_link = MANUAL_ROOT / "latest"
    if latest_link.exists() or latest_link.is_symlink():
        if latest_link.is_symlink() or latest_link.is_file():
            latest_link.unlink()
        else:
            shutil.rmtree(latest_link)
    latest_link.symlink_to(output_dir, target_is_directory=True)

    camera_xyz = " ".join(f"{value:.6f}" for value in camera_state.xyz)
    camera_rpy = " ".join(f"{value:.6f}" for value in camera_state.rpy_deg)
    lidar_xyz = " ".join(f"{value:.6f}" for value in lidar_state.xyz)
    lidar_rpy = " ".join(f"{value:.6f}" for value in lidar_state.rpy_deg)

    manual_env = output_dir / "manual_sensor_extrinsics.env"
    camera_env = output_dir / "camera_manual_extrinsics.env"
    lidar_env = output_dir / "lidar_manual_extrinsics.env"
    camera_best_env = output_dir / "camera_best_extrinsics_compatible.env"

    write_env_file(
        manual_env,
        {
            "CAMERA_FRAME": camera_frame,
            "CAMERA_XYZ": camera_xyz,
            "CAMERA_RPY": camera_rpy,
            "LIDAR_FRAME": lidar_frame,
            "LIDAR_XYZ": lidar_xyz,
            "LIDAR_RPY": lidar_rpy,
        },
    )
    write_env_file(
        camera_env,
        {
            "CAMERA_FRAME": camera_frame,
            "CAMERA_XYZ": camera_xyz,
            "CAMERA_RPY": camera_rpy,
        },
    )
    write_env_file(
        lidar_env,
        {
            "LIDAR_FRAME": lidar_frame,
            "LIDAR_XYZ": lidar_xyz,
            "LIDAR_RPY": lidar_rpy,
        },
    )
    write_env_file(
        camera_best_env,
        {
            "X": f"{camera_state.xyz[0]:.6f}",
            "Y": f"{camera_state.xyz[1]:.6f}",
            "Z": f"{camera_state.xyz[2]:.6f}",
            "ROLL_DEG": f"{camera_state.rpy_deg[0]:.6f}",
            "PITCH_DEG": f"{camera_state.rpy_deg[1]:.6f}",
            "YAW_DEG": f"{camera_state.rpy_deg[2]:.6f}",
        },
    )
    return [manual_env, camera_env, lidar_env, camera_best_env]


def print_help() -> None:
    print(
        "\nManual sensor extrinsics calibration\n"
        "Hotkeys:\n"
        "  1/2/3   step size fine / medium / coarse\n"
        "  TAB     switch active sensor (camera / lidar)\n"
        "  q/a     x +/-\n"
        "  w/s     y +/-\n"
        "  e/d     z +/-\n"
        "  r/f     roll +/-\n"
        "  t/g     pitch +/-\n"
        "  y/h     yaw +/-\n"
        "  p       save current values\n"
        "  ?       show help\n"
        "  x       exit\n"
    )


def print_status(
    active_sensor: str,
    step_size: StepSize,
    camera_frame: str,
    camera_state: ExtrinsicsState,
    lidar_frame: str,
    lidar_state: ExtrinsicsState,
) -> None:
    print(
        "\n"
        f"Active sensor: {active_sensor} | step={step_size.name} "
        f"({step_size.translation_m:.3f} m / {step_size.rotation_deg:.1f} deg)\n"
        f"camera {camera_frame}: xyz=({camera_state.xyz[0]: .4f}, {camera_state.xyz[1]: .4f}, {camera_state.xyz[2]: .4f}) "
        f"rpy_deg=({camera_state.rpy_deg[0]: .3f}, {camera_state.rpy_deg[1]: .3f}, {camera_state.rpy_deg[2]: .3f})\n"
        f"lidar  {lidar_frame}: xyz=({lidar_state.xyz[0]: .4f}, {lidar_state.xyz[1]: .4f}, {lidar_state.xyz[2]: .4f}) "
        f"rpy_deg=({lidar_state.rpy_deg[0]: .3f}, {lidar_state.rpy_deg[1]: .3f}, {lidar_state.rpy_deg[2]: .3f})\n",
        flush=True,
    )


def update_state(state: ExtrinsicsState, key: str, step_size: StepSize) -> bool:
    if key == "q":
        state.xyz[0] += step_size.translation_m
    elif key == "a":
        state.xyz[0] -= step_size.translation_m
    elif key == "w":
        state.xyz[1] += step_size.translation_m
    elif key == "s":
        state.xyz[1] -= step_size.translation_m
    elif key == "e":
        state.xyz[2] += step_size.translation_m
    elif key == "d":
        state.xyz[2] -= step_size.translation_m
    elif key == "r":
        state.rpy_deg[0] += step_size.rotation_deg
    elif key == "f":
        state.rpy_deg[0] -= step_size.rotation_deg
    elif key == "t":
        state.rpy_deg[1] += step_size.rotation_deg
    elif key == "g":
        state.rpy_deg[1] -= step_size.rotation_deg
    elif key == "y":
        state.rpy_deg[2] += step_size.rotation_deg
    elif key == "h":
        state.rpy_deg[2] -= step_size.rotation_deg
    else:
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interactive manual TF helper for base_link -> camera_link and base_link -> lidar frame."
    )
    parser.add_argument("--base-frame", default="base_link")
    parser.add_argument("--camera-frame", default="camera_link")
    parser.add_argument("--lidar-frame", default="lidar_frame")
    parser.add_argument("--output-dir", default=str(MANUAL_ROOT / time.strftime("%Y%m%d_%H%M%S")))
    parser.add_argument("--publish-rate", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not sys.stdin.isatty():
        print("[manual_sensor_extrinsics] ERROR: interactive TTY required for keyboard control.", file=sys.stderr)
        return 2

    logs: list[str] = []
    camera_state = load_initial_camera_state(logs)
    lidar_frame, lidar_state = load_initial_lidar_state(args.lidar_frame, logs)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for line in logs:
        print(f"[manual_sensor_extrinsics] {line}")

    print(
        "[manual_sensor_extrinsics] "
        f"output_dir={output_dir} base_frame={args.base_frame} "
        f"camera_frame={args.camera_frame} lidar_frame={lidar_frame}"
    )

    rclpy.init()
    node = ManualExtrinsicsPublisher(args.base_frame, args.camera_frame, lidar_frame)
    active_sensor = "camera"
    step_index = 1
    publish_period = 1.0 / max(args.publish_rate, 1.0)
    node.publish_state(camera_state, lidar_state)
    last_publish = time.monotonic()

    print_help()
    print_status(active_sensor, STEP_SIZES[step_index], args.camera_frame, camera_state, lidar_frame, lidar_state)

    try:
        with RawTerminal():
            while rclpy.ok():
                now = time.monotonic()
                if now - last_publish >= publish_period:
                    node.publish_state(camera_state, lidar_state)
                    last_publish = now

                rclpy.spin_once(node, timeout_sec=0.0)
                ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                if not ready:
                    continue

                key = sys.stdin.read(1)
                if key == "\t":
                    active_sensor = "lidar" if active_sensor == "camera" else "camera"
                    print_status(
                        active_sensor,
                        STEP_SIZES[step_index],
                        args.camera_frame,
                        camera_state,
                        lidar_frame,
                        lidar_state,
                    )
                    continue
                if key in {"1", "2", "3"}:
                    step_index = int(key) - 1
                    print_status(
                        active_sensor,
                        STEP_SIZES[step_index],
                        args.camera_frame,
                        camera_state,
                        lidar_frame,
                        lidar_state,
                    )
                    continue
                if key == "?":
                    print_help()
                    print_status(
                        active_sensor,
                        STEP_SIZES[step_index],
                        args.camera_frame,
                        camera_state,
                        lidar_frame,
                        lidar_state,
                    )
                    continue
                if key == "p":
                    saved = save_current_values(output_dir, args.camera_frame, lidar_frame, camera_state, lidar_state)
                    print("[manual_sensor_extrinsics] saved:")
                    for path in saved:
                        print(f"  {path}")
                    continue
                if key == "x":
                    print("[manual_sensor_extrinsics] exit requested")
                    break

                target_state = camera_state if active_sensor == "camera" else lidar_state
                if update_state(target_state, key, STEP_SIZES[step_index]):
                    print_status(
                        active_sensor,
                        STEP_SIZES[step_index],
                        args.camera_frame,
                        camera_state,
                        lidar_frame,
                        lidar_state,
                    )
    finally:
        node.destroy_node()
        rclpy.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
