#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
BAGS_ROOT = REPO_ROOT / "artifacts" / "bags"
OUTPUT_ROOT = REPO_ROOT / "artifacts" / "calibration" / "camera_mount"
LATEST_LINK = OUTPUT_ROOT / "latest"

DEPTH_TOPIC = "/camera/realsense2_camera/aligned_depth_to_color/image_raw"
CAMERA_INFO_TOPIC = "/camera/realsense2_camera/color/camera_info"
COLOR_TOPIC = "/camera/realsense2_camera/color/image_raw"
ODOM_TOPIC = "/utlidar/robot_odom"
TF_TOPIC = "/tf"
TF_STATIC_TOPIC = "/tf_static"
SCAN_TOPIC = "/scan"

REPLAY_TF_CLOCK_MISMATCH_PATTERNS = (
    "Lookup would require extrapolation into the past",
    "TF_OLD_DATA",
)

BOOTSTRAP_SAMPLE_PERIOD_SEC = 0.5
MAX_BOOTSTRAP_FRAMES = 20
DEPTH_MIN_METERS = 0.45
DEPTH_MAX_METERS = 4.0
DEPTH_DOWNSAMPLE_STEP = 8
PLANE_RANSAC_ITERATIONS = 180
PLANE_INLIER_THRESHOLD = 0.03
MIN_PLANE_INLIERS = 400
MIN_BOOTSTRAP_PLANE_FRAMES = 3
WALL_FLOOR_MIN_ANGLE_DEG = 60.0

SEARCH_SPACE = {
    "x": (0.20, 0.40),
    "y": (-0.02, 0.02),
    "z": (0.30, 0.40),
    "roll_deg": (-2.0, 2.0),
    "pitch_deg": (-20.0, -2.0),
    "yaw_deg": (-3.0, 3.0),
}

PRIOR_CENTER = {
    "x": 0.30,
    "y": 0.0,
    "z": 0.35,
    "roll_deg": 0.0,
    "pitch_deg": -8.0,
    "yaw_deg": 0.0,
}

PRIOR_SIGMA = {
    "x": 0.05,
    "y": 0.005,
    "z": 0.03,
    "roll_deg": 0.6,
    "pitch_deg": 4.0,
    "yaw_deg": 1.0,
}

FAST_SCORE_WEIGHTS = {
    "floor_normal_consistency": 2.5,
    "floor_offset_consistency": 1.5,
    "wall_normal_consistency": 2.0,
    "wall_offset_consistency": 1.0,
    "prior_penalty": 1.0,
}

END_SCORE_WEIGHTS = {
    "map_sharpness": 0.35,
    "wall_straightness": 0.35,
    "warning_penalty": 0.20,
    "prior_penalty": 0.10,
    "scan_support": 0.05,
}


@dataclass
class TopicMeta:
    name: str
    type: str
    count: int


@dataclass
class BagSummary:
    path: Path
    duration_sec: float
    start_time_ns: int
    message_count: int
    topics: dict[str, TopicMeta]


@dataclass
class CameraModel:
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    frame_id: str


@dataclass
class PlaneDetection:
    normal: np.ndarray
    offset: float
    inliers: int
    centroid: np.ndarray
    label: str


@dataclass
class BootstrapFrame:
    stamp_ns: int
    floor_plane: PlaneDetection | None
    wall_plane: PlaneDetection | None
    odom_position: np.ndarray | None
    odom_rotation: Rotation | None


@dataclass
class BootstrapResult:
    success: bool
    frames_used: int
    floor_frames: int
    wall_frames: int
    wall_floor_frames: int
    camera_info_frame: str
    camera_link_frame: str | None
    optical_to_camera_link_rpy_deg: tuple[float, float, float] | None
    optical_to_camera_link_xyz: tuple[float, float, float] | None
    estimated_roll_deg: float | None
    estimated_pitch_deg: float | None
    estimated_yaw_deg: float | None
    estimated_camera_height_m: float | None
    bootstrap_center: dict[str, float]
    floor_detected: bool
    wall_detected: bool
    notes: list[str]
    frame_results: list[dict[str, Any]]


@dataclass
class CandidateResult:
    params: dict[str, float]
    stage_a_score: float
    stage_b_score: float | None
    final_score: float | None
    run_dir: Path | None
    status: str
    notes: list[str]


class CalibrationError(RuntimeError):
    pass


np = None
yaml = None
cv2 = None
Rotation = None


def require_numeric_stack():
    global np, Rotation
    if np is None or Rotation is None:
        try:
            import numpy as _np
            from scipy.spatial.transform import Rotation as _Rotation
        except Exception as exc:
            raise CalibrationError(
                "NumPy/SciPy are required for camera-mount calibration but are not importable "
                "in the current runtime context."
            ) from exc
        np = _np
        Rotation = _Rotation
    return np, Rotation


def require_yaml_module():
    global yaml
    if yaml is None:
        try:
            import yaml as _yaml
        except Exception as exc:
            raise CalibrationError(
                "PyYAML is required for calibration metadata and bag inspection but is not importable."
            ) from exc
        yaml = _yaml
    return yaml


def require_cv2_module():
    global cv2
    if cv2 is None:
        try:
            import cv2 as _cv2
        except Exception as exc:
            raise CalibrationError(
                "OpenCV (cv2) is required for Stage B map quality scoring but is not importable."
            ) from exc
        cv2 = _cv2
    return cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Best-effort offline calibration for base_link -> camera_link mount extrinsics."
    )
    parser.add_argument("--latest", action="store_true", default=True, help="Use latest bag (default).")
    parser.add_argument("--bootstrap-seconds", type=float, default=10.0)
    parser.add_argument("--fast-trials", type=int, default=40)
    parser.add_argument("--refine-trials", type=int, default=10)
    parser.add_argument("--use-scan-score", action="store_true", default=False)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only bag selection, bootstrap attempt, and search-space reporting.",
    )
    return parser.parse_args()


def require_optuna():
    try:
        import optuna
        from optuna.samplers import TPESampler
    except ModuleNotFoundError as exc:
        raise CalibrationError(
            "optuna is required for optimization but is not importable. "
            "Install it, for example with: pip install optuna"
        ) from exc
    return optuna, TPESampler


def require_rosbag_modules():
    try:
        import rosbag2_py
        from rclpy.serialization import deserialize_message
        from rosidl_runtime_py.utilities import get_message
    except ModuleNotFoundError as exc:
        raise CalibrationError(
            "ROS2 Python bag-reading modules are not importable. "
            "Run this script in the ROS2 Humble environment where rosbag2_py and rclpy are available."
        ) from exc
    return rosbag2_py, deserialize_message, get_message


def eprint(msg: str) -> None:
    print(msg, flush=True)


def newest_valid_bag(root: Path) -> BagSummary:
    candidates = sorted(
        (path for path in root.glob("*") if path.is_dir() and (path / "metadata.yaml").is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise CalibrationError(f"No valid rosbag2 folders with metadata.yaml found under {root}.")
    return load_bag_summary(candidates[0])


def load_bag_summary(bag_dir: Path) -> BagSummary:
    yaml_mod = require_yaml_module()
    metadata_path = bag_dir / "metadata.yaml"
    data = yaml_mod.safe_load(metadata_path.read_text(encoding="utf-8"))
    info = data["rosbag2_bagfile_information"]
    topics = {}
    for entry in info.get("topics_with_message_count", []):
        meta = entry["topic_metadata"]
        topics[meta["name"]] = TopicMeta(
            name=meta["name"], type=meta["type"], count=int(entry["message_count"])
        )
    return BagSummary(
        path=bag_dir,
        duration_sec=info["duration"]["nanoseconds"] / 1e9,
        start_time_ns=int(info["starting_time"]["nanoseconds_since_epoch"]),
        message_count=int(info["message_count"]),
        topics=topics,
    )


def make_output_dirs() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def update_latest_symlink(run_dir: Path) -> None:
    if LATEST_LINK.is_symlink() or LATEST_LINK.exists():
        if LATEST_LINK.is_dir() and not LATEST_LINK.is_symlink():
            shutil.rmtree(LATEST_LINK)
        else:
            LATEST_LINK.unlink()
    LATEST_LINK.symlink_to(run_dir.name)


def find_db_files(bag_summary: BagSummary) -> list[Path]:
    return sorted(
        [
            path
            for path in bag_summary.path.iterdir()
            if path.suffix in {".db3", ".sqlite3"} and path.is_file()
        ]
    )


def open_reader(bag_summary: BagSummary):
    rosbag2_py, deserialize_message, get_message = require_rosbag_modules()
    reader = rosbag2_py.SequentialReader()
    storage_options = rosbag2_py.StorageOptions(uri=str(bag_summary.path), storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )
    reader.open(storage_options, converter_options)
    topic_types = {
        entry.name: entry.type for entry in reader.get_all_topics_and_types()
    }
    return reader, topic_types, deserialize_message, get_message


def iter_deserialized_messages(
    bag_summary: BagSummary,
    topics: set[str],
    end_time_ns: int | None = None,
) -> Iterable[tuple[str, Any, int]]:
    reader, topic_types, deserialize_message, get_message = open_reader(bag_summary)
    msg_classes: dict[str, Any] = {}
    while reader.has_next():
        topic_name, raw_data, timestamp = reader.read_next()
        if end_time_ns is not None and timestamp > end_time_ns:
            break
        if topic_name not in topics:
            continue
        if topic_name not in msg_classes:
            if topic_name not in topic_types:
                raise CalibrationError(f"Topic type missing for {topic_name} in bag.")
            msg_classes[topic_name] = get_message(topic_types[topic_name])
        yield topic_name, deserialize_message(raw_data, msg_classes[topic_name]), timestamp


def image_to_depth_meters(msg: Any) -> np.ndarray:
    data = np.frombuffer(msg.data, dtype=np.uint8)
    if msg.encoding in {"16UC1", "mono16"}:
        depth = data.view(np.uint16).reshape((msg.height, msg.width)).astype(np.float32) / 1000.0
    elif msg.encoding == "32FC1":
        depth = data.view(np.float32).reshape((msg.height, msg.width))
    else:
        raise CalibrationError(f"Unsupported depth encoding for bootstrap: {msg.encoding}")
    depth = np.where(np.isfinite(depth), depth, 0.0)
    return depth


def camera_model_from_msg(msg: Any) -> CameraModel:
    return CameraModel(
        width=int(msg.width),
        height=int(msg.height),
        fx=float(msg.k[0]),
        fy=float(msg.k[4]),
        cx=float(msg.k[2]),
        cy=float(msg.k[5]),
        frame_id=str(msg.header.frame_id),
    )


def depth_to_points(depth: np.ndarray, model: CameraModel) -> np.ndarray:
    sampled = depth[::DEPTH_DOWNSAMPLE_STEP, ::DEPTH_DOWNSAMPLE_STEP]
    valid = (sampled >= DEPTH_MIN_METERS) & (sampled <= DEPTH_MAX_METERS)
    if not np.any(valid):
        return np.empty((0, 3), dtype=np.float32)
    ys, xs = np.indices(sampled.shape)
    xs = xs.astype(np.float32) * DEPTH_DOWNSAMPLE_STEP
    ys = ys.astype(np.float32) * DEPTH_DOWNSAMPLE_STEP
    z = sampled[valid]
    x = (xs[valid] - model.cx) * z / model.fx
    y = (ys[valid] - model.cy) * z / model.fy
    return np.column_stack((x, y, z)).astype(np.float32)


def fit_plane_from_points(points: np.ndarray) -> tuple[np.ndarray, float] | None:
    if points.shape[0] < 3:
        return None
    p0, p1, p2 = points[:3]
    normal = np.cross(p1 - p0, p2 - p0)
    norm = np.linalg.norm(normal)
    if norm < 1e-9:
        return None
    normal = normal / norm
    offset = -float(np.dot(normal, p0))
    return normal, offset


def plane_distances(points: np.ndarray, normal: np.ndarray, offset: float) -> np.ndarray:
    return np.abs(points @ normal + offset)


def ransac_plane(points: np.ndarray, rng: np.random.Generator) -> PlaneDetection | None:
    if points.shape[0] < MIN_PLANE_INLIERS:
        return None
    best_indices: np.ndarray | None = None
    best_model: tuple[np.ndarray, float] | None = None
    count = points.shape[0]
    for _ in range(PLANE_RANSAC_ITERATIONS):
        sample_idx = rng.choice(count, size=3, replace=False)
        model = fit_plane_from_points(points[sample_idx])
        if model is None:
            continue
        normal, offset = model
        distances = plane_distances(points, normal, offset)
        inliers = np.nonzero(distances < PLANE_INLIER_THRESHOLD)[0]
        if best_indices is None or inliers.size > best_indices.size:
            best_indices = inliers
            best_model = model
    if best_indices is None or best_model is None or best_indices.size < MIN_PLANE_INLIERS:
        return None
    inlier_points = points[best_indices]
    refined_normal, refined_offset = refine_plane_svd(inlier_points)
    if refined_normal is None:
        return None
    centroid = np.mean(inlier_points, axis=0)
    if np.dot(refined_normal, centroid) > 0:
        refined_normal = -refined_normal
        refined_offset = -refined_offset
    return PlaneDetection(
        normal=refined_normal,
        offset=float(refined_offset),
        inliers=int(best_indices.size),
        centroid=centroid,
        label="candidate",
    )


def refine_plane_svd(points: np.ndarray) -> tuple[np.ndarray | None, float | None]:
    if points.shape[0] < 3:
        return None, None
    centroid = np.mean(points, axis=0)
    centered = points - centroid
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    normal = vt[-1]
    norm = np.linalg.norm(normal)
    if norm < 1e-9:
        return None, None
    normal = normal / norm
    offset = -float(np.dot(normal, centroid))
    return normal, offset


def detect_floor_and_wall(points: np.ndarray, rng: np.random.Generator) -> tuple[PlaneDetection | None, PlaneDetection | None]:
    first = ransac_plane(points, rng)
    if first is None:
        return None, None
    mask = plane_distances(points, first.normal, first.offset) >= PLANE_INLIER_THRESHOLD
    remaining = points[mask]
    second = ransac_plane(remaining, rng)
    planes = [plane for plane in [first, second] if plane is not None]
    if not planes:
        return None, None
    floor = max(planes, key=lambda plane: abs(float(plane.normal[1])))
    floor.label = "floor"
    wall = None
    for plane in planes:
        if plane is floor:
            continue
        angle_deg = math.degrees(
            math.acos(
                float(np.clip(abs(np.dot(plane.normal, floor.normal)), 0.0, 1.0))
            )
        )
        if angle_deg >= WALL_FLOOR_MIN_ANGLE_DEG and abs(float(plane.normal[2])) >= abs(float(plane.normal[1])):
            wall = plane
            break
    if wall is not None:
        wall.label = "wall"
    return floor, wall


def extract_static_transforms(bag_summary: BagSummary, max_time_ns: int) -> dict[tuple[str, str], tuple[np.ndarray, Rotation]]:
    transforms: dict[tuple[str, str], tuple[np.ndarray, Rotation]] = {}
    topics = {TF_STATIC_TOPIC, TF_TOPIC}
    try:
        iterator = iter_deserialized_messages(bag_summary, topics, end_time_ns=max_time_ns)
    except CalibrationError:
        return transforms
    for topic_name, msg, _ in iterator:
        if topic_name not in {TF_STATIC_TOPIC, TF_TOPIC}:
            continue
        for transform in getattr(msg, "transforms", []):
            parent = str(transform.header.frame_id)
            child = str(transform.child_frame_id)
            translation = np.array(
                [
                    float(transform.transform.translation.x),
                    float(transform.transform.translation.y),
                    float(transform.transform.translation.z),
                ],
                dtype=np.float64,
            )
            rotation = Rotation.from_quat(
                [
                    float(transform.transform.rotation.x),
                    float(transform.transform.rotation.y),
                    float(transform.transform.rotation.z),
                    float(transform.transform.rotation.w),
                ]
            )
            transforms[(parent, child)] = (translation, rotation)
    return transforms


def lookup_static_chain(
    transforms: dict[tuple[str, str], tuple[np.ndarray, Rotation]],
    parent: str,
    child: str,
) -> tuple[np.ndarray, Rotation] | None:
    if parent == child:
        return np.zeros(3, dtype=np.float64), Rotation.identity()
    visited: set[str] = set()
    queue: list[tuple[str, np.ndarray, Rotation]] = [(parent, np.zeros(3), Rotation.identity())]
    adjacency: dict[str, list[tuple[str, np.ndarray, Rotation]]] = {}
    for (src, dst), (translation, rotation) in transforms.items():
        adjacency.setdefault(src, []).append((dst, translation, rotation))
        inv_rotation = rotation.inv()
        inv_translation = -inv_rotation.apply(translation)
        adjacency.setdefault(dst, []).append((src, inv_translation, inv_rotation))
    while queue:
        frame, translation, rotation = queue.pop(0)
        if frame == child:
            return translation, rotation
        if frame in visited:
            continue
        visited.add(frame)
        for next_frame, edge_translation, edge_rotation in adjacency.get(frame, []):
            queue.append(
                (
                    next_frame,
                    translation + rotation.apply(edge_translation),
                    rotation * edge_rotation,
                )
            )
    return None


def gather_bootstrap_data(
    bag_summary: BagSummary,
    bootstrap_seconds: float,
) -> tuple[CameraModel | None, list[BootstrapFrame], dict[tuple[str, str], tuple[np.ndarray, Rotation]]]:
    end_time_ns = bag_summary.start_time_ns + int(bootstrap_seconds * 1e9)
    required_topics = {DEPTH_TOPIC, CAMERA_INFO_TOPIC, ODOM_TOPIC, TF_TOPIC, TF_STATIC_TOPIC}
    available_topics = set(bag_summary.topics)
    ros_topics = available_topics & required_topics
    if DEPTH_TOPIC not in available_topics or CAMERA_INFO_TOPIC not in available_topics:
        return None, [], extract_static_transforms(bag_summary, end_time_ns)

    rng = np.random.default_rng(7)
    camera_model: CameraModel | None = None
    odom_samples: list[tuple[int, np.ndarray, Rotation]] = []
    frames: list[BootstrapFrame] = []
    last_frame_time_ns = -1

    for topic_name, msg, timestamp in iter_deserialized_messages(
        bag_summary, ros_topics, end_time_ns=end_time_ns
    ):
        if topic_name == CAMERA_INFO_TOPIC and camera_model is None:
            camera_model = camera_model_from_msg(msg)
        elif topic_name == ODOM_TOPIC:
            odom_samples.append(
                (
                    timestamp,
                    np.array(
                        [
                            float(msg.pose.pose.position.x),
                            float(msg.pose.pose.position.y),
                            float(msg.pose.pose.position.z),
                        ],
                        dtype=np.float64,
                    ),
                    Rotation.from_quat(
                        [
                            float(msg.pose.pose.orientation.x),
                            float(msg.pose.pose.orientation.y),
                            float(msg.pose.pose.orientation.z),
                            float(msg.pose.pose.orientation.w),
                        ]
                    ),
                )
            )
        elif topic_name == DEPTH_TOPIC:
            if camera_model is None:
                continue
            if last_frame_time_ns >= 0 and timestamp - last_frame_time_ns < int(
                BOOTSTRAP_SAMPLE_PERIOD_SEC * 1e9
            ):
                continue
            if len(frames) >= MAX_BOOTSTRAP_FRAMES:
                continue
            last_frame_time_ns = timestamp
            depth = image_to_depth_meters(msg)
            points = depth_to_points(depth, camera_model)
            floor_plane, wall_plane = detect_floor_and_wall(points, rng)
            odom_position, odom_rotation = nearest_odom(odom_samples, timestamp)
            frames.append(
                BootstrapFrame(
                    stamp_ns=timestamp,
                    floor_plane=floor_plane,
                    wall_plane=wall_plane,
                    odom_position=odom_position,
                    odom_rotation=odom_rotation,
                )
            )
    return camera_model, frames, extract_static_transforms(bag_summary, end_time_ns)


def nearest_odom(
    odom_samples: list[tuple[int, np.ndarray, Rotation]],
    stamp_ns: int,
) -> tuple[np.ndarray | None, Rotation | None]:
    if not odom_samples:
        return None, None
    nearest = min(odom_samples, key=lambda sample: abs(sample[0] - stamp_ns))
    return nearest[1], nearest[2]


def build_bootstrap_result(
    camera_model: CameraModel | None,
    frames: list[BootstrapFrame],
    static_transforms: dict[tuple[str, str], tuple[np.ndarray, Rotation]],
) -> BootstrapResult:
    notes: list[str] = []
    if camera_model is None:
        notes.append("Missing camera_info or required camera topics in latest bag.")
        return BootstrapResult(
            success=False,
            frames_used=0,
            floor_frames=0,
            wall_frames=0,
            wall_floor_frames=0,
            camera_info_frame="",
            camera_link_frame=None,
            optical_to_camera_link_rpy_deg=None,
            optical_to_camera_link_xyz=None,
            estimated_roll_deg=None,
            estimated_pitch_deg=None,
            estimated_yaw_deg=None,
            estimated_camera_height_m=None,
            bootstrap_center=PRIOR_CENTER.copy(),
            floor_detected=False,
            wall_detected=False,
            notes=notes,
            frame_results=[],
        )

    chain = lookup_static_chain(static_transforms, "camera_link", camera_model.frame_id)
    optical_to_camera_link_xyz = None
    optical_to_camera_link_rpy = None
    optical_to_camera_link_rotation = Rotation.identity()
    camera_link_frame = None
    if chain is not None:
        translation, rotation = chain
        optical_to_camera_link_xyz = tuple(float(v) for v in translation.tolist())
        optical_to_camera_link_rpy = tuple(float(v) for v in rotation.as_euler("xyz", degrees=True))
        optical_to_camera_link_rotation = rotation
        camera_link_frame = "camera_link"
    else:
        notes.append(
            f"Static transform chain camera_link -> {camera_model.frame_id} not found in bag TF; "
            "bootstrap operates in camera_info frame and falls back to priors for final mount alignment."
        )

    floor_frames = 0
    wall_frames = 0
    wall_floor_frames = 0
    frame_results: list[dict[str, Any]] = []
    floor_normals: list[np.ndarray] = []
    wall_normals: list[np.ndarray] = []
    floor_offsets: list[float] = []

    for frame in frames:
        floor_plane = transform_plane(frame.floor_plane, optical_to_camera_link_rotation)
        wall_plane = transform_plane(frame.wall_plane, optical_to_camera_link_rotation)
        if floor_plane is not None:
            floor_frames += 1
            floor_normals.append(floor_plane.normal)
            floor_offsets.append(abs(floor_plane.offset))
        if wall_plane is not None:
            wall_frames += 1
            wall_normals.append(wall_plane.normal)
        if floor_plane is not None and wall_plane is not None:
            wall_floor_frames += 1
        frame_results.append(
            {
                "stamp_ns": int(frame.stamp_ns),
                "floor_inliers": int(floor_plane.inliers) if floor_plane else 0,
                "wall_inliers": int(wall_plane.inliers) if wall_plane else 0,
                "floor_detected": bool(floor_plane),
                "wall_detected": bool(wall_plane),
            }
        )

    bootstrap_center = PRIOR_CENTER.copy()
    estimated_roll = None
    estimated_pitch = None
    estimated_yaw = None
    estimated_height = None
    success = False

    if wall_floor_frames >= MIN_BOOTSTRAP_PLANE_FRAMES:
        floor_normal = normalize(np.mean(floor_normals, axis=0))
        wall_normal = normalize(np.mean(wall_normals, axis=0))
        rotation_guess = estimate_mount_rotation_from_planes(floor_normal, wall_normal)
        if rotation_guess is not None:
            roll_deg, pitch_deg, yaw_deg = rotation_guess.as_euler("xyz", degrees=True)
            estimated_roll = clamp(float(roll_deg), *SEARCH_SPACE["roll_deg"])
            estimated_pitch = clamp(float(pitch_deg), *SEARCH_SPACE["pitch_deg"])
            estimated_yaw = clamp(float(yaw_deg), *SEARCH_SPACE["yaw_deg"])
            estimated_height = clamp(float(np.median(floor_offsets)), *SEARCH_SPACE["z"])
            bootstrap_center.update(
                {
                    "roll_deg": estimated_roll,
                    "pitch_deg": estimated_pitch,
                    "yaw_deg": estimated_yaw,
                    "z": estimated_height,
                }
            )
            success = True
    else:
        notes.append(
            "Robust wall+floor bootstrap was not available in the first bootstrap window; falling back to priors."
        )

    return BootstrapResult(
        success=success,
        frames_used=len(frames),
        floor_frames=floor_frames,
        wall_frames=wall_frames,
        wall_floor_frames=wall_floor_frames,
        camera_info_frame=camera_model.frame_id,
        camera_link_frame=camera_link_frame,
        optical_to_camera_link_rpy_deg=optical_to_camera_link_rpy,
        optical_to_camera_link_xyz=optical_to_camera_link_xyz,
        estimated_roll_deg=estimated_roll,
        estimated_pitch_deg=estimated_pitch,
        estimated_yaw_deg=estimated_yaw,
        estimated_camera_height_m=estimated_height,
        bootstrap_center=bootstrap_center,
        floor_detected=floor_frames >= MIN_BOOTSTRAP_PLANE_FRAMES,
        wall_detected=wall_frames >= MIN_BOOTSTRAP_PLANE_FRAMES,
        notes=notes,
        frame_results=frame_results,
    )


def transform_plane(plane: PlaneDetection | None, rotation: Rotation) -> PlaneDetection | None:
    if plane is None:
        return None
    normal = rotation.apply(plane.normal)
    centroid = rotation.apply(plane.centroid)
    offset = -float(np.dot(normal, centroid))
    return PlaneDetection(
        normal=normal,
        offset=offset,
        inliers=plane.inliers,
        centroid=centroid,
        label=plane.label,
    )


def estimate_mount_rotation_from_planes(
    floor_normal: np.ndarray, wall_normal: np.ndarray
) -> Rotation | None:
    z_axis = -normalize(floor_normal)
    wall_proj = wall_normal - np.dot(wall_normal, z_axis) * z_axis
    if np.linalg.norm(wall_proj) < 1e-6:
        return None
    x_axis = normalize(-wall_proj)
    y_axis = normalize(np.cross(z_axis, x_axis))
    if np.linalg.norm(y_axis) < 1e-6:
        return None
    x_axis = normalize(np.cross(y_axis, z_axis))
    matrix = np.column_stack((x_axis, y_axis, z_axis))
    return Rotation.from_matrix(matrix)


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm < 1e-9:
        return vector
    return vector / norm


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def prior_penalty(params: dict[str, float], bootstrap_center: dict[str, float]) -> float:
    total = 0.0
    centers = PRIOR_CENTER.copy()
    centers.update(bootstrap_center)
    for key, value in params.items():
        sigma = PRIOR_SIGMA[key]
        total += ((value - centers[key]) / sigma) ** 2
    if params["x"] < 0.20:
        total += 100.0
    return total


def make_fast_objective(
    frames: list[BootstrapFrame],
    bootstrap: BootstrapResult,
    optical_chain: tuple[np.ndarray, Rotation] | None,
):
    optical_translation = np.zeros(3, dtype=np.float64)
    optical_rotation = Rotation.identity()
    if optical_chain is not None:
        optical_translation, optical_rotation = optical_chain

    def objective(trial: Any) -> float:
        params = {
            "x": trial.suggest_float("x", *SEARCH_SPACE["x"]),
            "y": trial.suggest_float("y", *SEARCH_SPACE["y"]),
            "z": trial.suggest_float("z", *SEARCH_SPACE["z"]),
            "roll_deg": trial.suggest_float("roll_deg", *SEARCH_SPACE["roll_deg"]),
            "pitch_deg": trial.suggest_float("pitch_deg", *SEARCH_SPACE["pitch_deg"]),
            "yaw_deg": trial.suggest_float("yaw_deg", *SEARCH_SPACE["yaw_deg"]),
        }
        base_to_camera_link = transform_from_params(params)
        base_to_optical_rotation = base_to_camera_link[1] * optical_rotation
        base_to_optical_translation = (
            base_to_camera_link[0] + base_to_camera_link[1].apply(optical_translation)
        )

        floor_normals: list[np.ndarray] = []
        wall_normals: list[np.ndarray] = []
        floor_offsets: list[float] = []
        wall_offsets: list[float] = []
        for frame in frames:
            if frame.odom_position is None or frame.odom_rotation is None:
                continue
            if frame.floor_plane is not None:
                world_normal, world_offset = plane_to_world(
                    frame.floor_plane,
                    frame.odom_position,
                    frame.odom_rotation,
                    base_to_optical_translation,
                    base_to_optical_rotation,
                )
                floor_normals.append(world_normal)
                floor_offsets.append(world_offset)
            if frame.wall_plane is not None:
                world_normal, world_offset = plane_to_world(
                    frame.wall_plane,
                    frame.odom_position,
                    frame.odom_rotation,
                    base_to_optical_translation,
                    base_to_optical_rotation,
                )
                wall_normals.append(world_normal)
                wall_offsets.append(world_offset)

        floor_normal_consistency = angular_variance(floor_normals)
        wall_normal_consistency = angular_variance(wall_normals)
        floor_offset_consistency = float(np.std(floor_offsets)) if len(floor_offsets) >= 2 else 1.0
        wall_offset_consistency = float(np.std(wall_offsets)) if len(wall_offsets) >= 2 else 1.0
        penalty = prior_penalty(params, bootstrap.bootstrap_center)

        fast_score = (
            FAST_SCORE_WEIGHTS["floor_normal_consistency"] / (1.0 + floor_normal_consistency)
            + FAST_SCORE_WEIGHTS["floor_offset_consistency"] / (1.0 + floor_offset_consistency)
            + FAST_SCORE_WEIGHTS["wall_normal_consistency"] / (1.0 + wall_normal_consistency)
            + FAST_SCORE_WEIGHTS["wall_offset_consistency"] / (1.0 + wall_offset_consistency)
            - FAST_SCORE_WEIGHTS["prior_penalty"] * penalty
        )
        trial.set_user_attr("fast_score", fast_score)
        trial.set_user_attr("prior_penalty", penalty)
        return fast_score

    return objective


def transform_from_params(params: dict[str, float]) -> tuple[np.ndarray, Rotation]:
    translation = np.array([params["x"], params["y"], params["z"]], dtype=np.float64)
    rotation = Rotation.from_euler(
        "xyz",
        [params["roll_deg"], params["pitch_deg"], params["yaw_deg"]],
        degrees=True,
    )
    return translation, rotation


def plane_to_world(
    plane: PlaneDetection,
    odom_position: np.ndarray,
    odom_rotation: Rotation,
    base_to_optical_translation: np.ndarray,
    base_to_optical_rotation: Rotation,
) -> tuple[np.ndarray, float]:
    plane_normal_base = base_to_optical_rotation.apply(plane.normal)
    plane_centroid_base = base_to_optical_translation + base_to_optical_rotation.apply(plane.centroid)
    plane_normal_world = odom_rotation.apply(plane_normal_base)
    plane_centroid_world = odom_position + odom_rotation.apply(plane_centroid_base)
    offset_world = -float(np.dot(plane_normal_world, plane_centroid_world))
    return plane_normal_world, offset_world


def angular_variance(normals: list[np.ndarray]) -> float:
    if len(normals) < 2:
        return 999.0
    reference = normalize(np.mean(normals, axis=0))
    angles = []
    for normal in normals:
        dot = float(np.clip(abs(np.dot(reference, normalize(normal))), 0.0, 1.0))
        angles.append(math.degrees(math.acos(dot)))
    return float(np.mean(angles))


def export_map_from_db(db_path: Path, map_dir: Path) -> tuple[Path, Path]:
    reprocess = shutil.which("rtabmap-reprocess")
    info = shutil.which("rtabmap-info")
    if reprocess is None or info is None:
        raise CalibrationError(
            "rtabmap-reprocess and rtabmap-info are required for Stage B map export."
        )
    map_dir.mkdir(parents=True, exist_ok=True)
    temp_db = map_dir / "_reprocess_export.db"
    temp_pgm = map_dir / "_reprocess_export_map.pgm"
    params_dump = map_dir / "_db_params.ini"
    for path in [temp_db, temp_pgm, params_dump]:
        if path.exists():
            path.unlink()

    subprocess.run([reprocess, "-g2", str(db_path), str(temp_db)], check=True, cwd=map_dir)
    if not temp_pgm.exists():
        raise CalibrationError(f"Expected exported map image not found: {temp_pgm}")
    map_pgm = map_dir / "map.pgm"
    temp_pgm.replace(map_pgm)

    subprocess.run([info, "--dump", str(params_dump), str(db_path)], check=True, cwd=map_dir)
    resolution = None
    for line in params_dump.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("Grid/CellSize="):
            resolution = line.split("=", 1)[1].strip()
            break
    if not resolution:
        resolution = "0.05"
    map_yaml = map_dir / "map.yaml"
    map_yaml.write_text(
        "\n".join(
            [
                "image: map.pgm",
                f"resolution: {resolution}",
                "origin: [0.0, 0.0, 0.0]",
                "negate: 0",
                "occupied_thresh: 0.65",
                "free_thresh: 0.196",
                "",
            ]
        ),
        encoding="utf-8",
    )
    temp_db.unlink(missing_ok=True)
    params_dump.unlink(missing_ok=True)
    return map_pgm, map_yaml


def compute_map_quality_metrics(map_pgm: Path) -> tuple[float, float]:
    cv2_mod = require_cv2_module()
    require_numeric_stack()
    image = cv2_mod.imread(str(map_pgm), cv2_mod.IMREAD_GRAYSCALE)
    if image is None:
        return 0.0, 0.0
    sharpness = float(cv2_mod.Laplacian(image, cv2_mod.CV_32F).var())
    edges = cv2_mod.Canny(image, 50, 150)
    lines = cv2_mod.HoughLinesP(
        edges, 1, np.pi / 180.0, threshold=25, minLineLength=20, maxLineGap=5
    )
    if lines is None or len(lines) == 0:
        return sharpness, 0.0
    lengths = []
    straightness_votes = []
    for line in lines[:, 0]:
        x1, y1, x2, y2 = [float(v) for v in line]
        length = math.hypot(x2 - x1, y2 - y1)
        if length <= 1e-6:
            continue
        angle = abs(math.degrees(math.atan2(y2 - y1, x2 - x1))) % 90.0
        deviation = min(abs(angle), abs(90.0 - angle))
        lengths.append(length)
        straightness_votes.append(max(0.0, 1.0 - deviation / 15.0))
    if not lengths:
        return sharpness, 0.0
    wall_straightness = float(np.average(straightness_votes, weights=lengths))
    return sharpness, wall_straightness


def run_map_evaluator(map_dir: Path, run_dir: Path) -> dict[str, Any]:
    evaluator = REPO_ROOT / "scripts" / "rtabmap" / "evaluate_map_artifacts.py"
    result = subprocess.run(
        [sys.executable, str(evaluator), "--map-dir", str(map_dir), "--run-dir", str(run_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    parsed: dict[str, Any] = {}
    for line in result.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def scan_support_score(bag_summary: BagSummary) -> float:
    scan_meta = bag_summary.topics.get(SCAN_TOPIC)
    depth_meta = bag_summary.topics.get(DEPTH_TOPIC)
    if scan_meta is None or depth_meta is None or depth_meta.count == 0:
        return 0.0
    ratio = scan_meta.count / depth_meta.count
    return float(max(0.0, min(1.0, ratio)))


def wait_for_ros_nodes(
    ros2_path: str,
    required_nodes: list[str],
    timeout_sec: float,
) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        result = subprocess.run(
            [ros2_path, "node", "list"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            nodes = {line.strip() for line in result.stdout.splitlines() if line.strip()}
            if all(node in nodes for node in required_nodes):
                return True
        time.sleep(1.0)
    return False


def assert_rtabmap_db_sane(
    db_path: Path,
    context: str,
    artifact_dir: Path,
    log_paths: list[Path],
    output_log: Path | None = None,
) -> None:
    checker = REPO_ROOT / "scripts" / "rtabmap" / "check_rtabmap_db_sanity.py"
    result = subprocess.run(
        [
            sys.executable,
            str(checker),
            "--db",
            str(db_path),
            "--context",
            context,
            "--artifact-dir",
            str(artifact_dir),
            *sum([["--log-path", str(path)] for path in log_paths], []),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if output_log is not None:
        output_log.write_text((result.stdout or "") + (result.stderr or ""), encoding="utf-8")
    if result.returncode != 0:
        message = result.stdout.strip() or result.stderr.strip()
        raise CalibrationError(message)


def detect_replay_tf_clock_mismatch(log_paths: list[Path]) -> str | None:
    for log_path in log_paths:
        try:
            text = log_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in REPLAY_TF_CLOCK_MISMATCH_PATTERNS:
            if pattern in text:
                return str(log_path)
    return None


def run_stage_b_candidate(
    candidate_index: int,
    params: dict[str, float],
    bag_summary: BagSummary,
    bootstrap: BootstrapResult,
    run_dir: Path,
    use_scan_score: bool,
) -> CandidateResult:
    candidate_dir = run_dir / f"candidate_{candidate_index:02d}"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    notes: list[str] = []

    required_topics = {COLOR_TOPIC, DEPTH_TOPIC, CAMERA_INFO_TOPIC, ODOM_TOPIC}
    missing = [topic for topic in required_topics if topic not in bag_summary.topics]
    if missing:
        raise CalibrationError(
            f"Latest bag {bag_summary.path} is missing required Stage B topics: {', '.join(missing)}"
        )

    if bootstrap.camera_link_frame != "camera_link":
        raise CalibrationError(
            "camera_link -> optical static transform could not be resolved from bag TF; "
            "cannot run Stage B without inventing frame relations."
        )

    db_path = candidate_dir / "rtabmap.db"
    map_dir = candidate_dir / "map_artifacts"
    db_sanity_log = candidate_dir / "db_sanity.log"
    stdout_log = candidate_dir / "mapping.stdout.log"
    stderr_log = candidate_dir / "mapping.stderr.log"
    ros2_path = shutil.which("ros2")
    if ros2_path is None:
        raise CalibrationError("ros2 CLI not found in PATH; Stage B cannot run.")

    candidate_translation, _ = transform_from_params(params)
    optical_xyz = bootstrap.optical_to_camera_link_xyz or (0.0, 0.0, 0.0)
    optical_rpy = bootstrap.optical_to_camera_link_rpy_deg or (0.0, 0.0, 0.0)

    processes: list[subprocess.Popen[str]] = []
    try:
        with stdout_log.open("w", encoding="utf-8") as out, stderr_log.open("w", encoding="utf-8") as err:
            processes.append(
                subprocess.Popen(
                    [
                        ros2_path,
                        "run",
                        "go2_tf_tools",
                        "odom_to_tf_broadcaster",
                        "--ros-args",
                        "-p",
                        "use_sim_time:=true",
                        "-p",
                        f"odom_topic:={ODOM_TOPIC}",
                        "-p",
                        "parent_frame:=odom",
                        "-p",
                        "child_frame:=base_link",
                        "-p",
                        "stamp_source:=now",
                    ],
                    stdout=out,
                    stderr=err,
                    text=True,
                    cwd=REPO_ROOT,
                )
            )
            processes.append(
                subprocess.Popen(
                    [
                        ros2_path,
                        "run",
                        "tf2_ros",
                        "static_transform_publisher",
                        f"{candidate_translation[0]}",
                        f"{candidate_translation[1]}",
                        f"{candidate_translation[2]}",
                        f"{math.radians(params['roll_deg'])}",
                        f"{math.radians(params['pitch_deg'])}",
                        f"{math.radians(params['yaw_deg'])}",
                        "base_link",
                        "camera_link",
                        "--ros-args",
                        "-p",
                        "use_sim_time:=true",
                    ],
                    stdout=out,
                    stderr=err,
                    text=True,
                    cwd=REPO_ROOT,
                )
            )
            processes.append(
                subprocess.Popen(
                    [
                        ros2_path,
                        "run",
                        "tf2_ros",
                        "static_transform_publisher",
                        f"{optical_xyz[0]}",
                        f"{optical_xyz[1]}",
                        f"{optical_xyz[2]}",
                        f"{math.radians(optical_rpy[0])}",
                        f"{math.radians(optical_rpy[1])}",
                        f"{math.radians(optical_rpy[2])}",
                        "camera_link",
                        bootstrap.camera_info_frame,
                        "--ros-args",
                        "-p",
                        "use_sim_time:=true",
                    ],
                    stdout=out,
                    stderr=err,
                    text=True,
                    cwd=REPO_ROOT,
                )
            )
            processes.append(
                subprocess.Popen(
                    [
                        ros2_path,
                        "launch",
                        "launch/rtabmap_mapping.launch.py",
                        "use_sim_time:=true",
                        "subscribe_scan:=false",
                        f"database_path:={db_path}",
                        f"rgb_topic:={COLOR_TOPIC}",
                        f"depth_topic:={DEPTH_TOPIC}",
                        f"camera_info_topic:={CAMERA_INFO_TOPIC}",
                        "base_frame:=base_link",
                        "odom_frame:=odom",
                        "map_frame:=map",
                    ],
                    stdout=out,
                    stderr=err,
                    text=True,
                    cwd=REPO_ROOT,
                )
            )

            if not wait_for_ros_nodes(ros2_path, ["/rgbd_sync", "/rtabmap"], timeout_sec=20.0):
                raise CalibrationError(
                    f"Stage B candidate {candidate_index}: rtabmap mapping nodes did not become ready "
                    f"before replay. DB target={db_path}. Logs: {stdout_log}, {stderr_log}"
                )
            play_cmd = [
                ros2_path,
                "bag",
                "play",
                str(bag_summary.path),
                "--clock",
                "50.0",
                "--topics",
                COLOR_TOPIC,
                DEPTH_TOPIC,
                CAMERA_INFO_TOPIC,
                ODOM_TOPIC,
            ]
            play_proc = subprocess.Popen(
                play_cmd,
                stdout=out,
                stderr=err,
                text=True,
                cwd=REPO_ROOT,
            )
            play_rc = play_proc.wait(timeout=max(30.0, bag_summary.duration_sec * 2.0))
            if play_rc != 0:
                raise CalibrationError(f"ros2 bag play failed for candidate {candidate_index} (rc={play_rc}).")
            time.sleep(3.0)

        for proc in reversed(processes):
            terminate_process(proc)

        mismatch_log = detect_replay_tf_clock_mismatch([stdout_log, stderr_log])
        if mismatch_log is not None:
            db_sanity_log.write_text(
                "Replay TF/clock mismatch detected.\n"
                f"db_path={db_path}\n"
                f"log_path={mismatch_log}\n"
                f"candidate_dir={candidate_dir}\n",
                encoding="utf-8",
            )
            raise CalibrationError(
                "Replay TF/clock mismatch detected. "
                f"DB target={db_path}. Candidate dir={candidate_dir}. "
                f"See {mismatch_log} and {db_sanity_log}"
            )

        if not db_path.exists():
            raise CalibrationError(f"Stage B candidate DB not produced: {db_path}")
        assert_rtabmap_db_sane(
            db_path,
            context=f"Stage B candidate {candidate_index}",
            artifact_dir=candidate_dir,
            log_paths=[stdout_log, stderr_log],
            output_log=db_sanity_log,
        )

        map_pgm, _ = export_map_from_db(db_path, map_dir)
        evaluator_data = run_map_evaluator(map_dir, candidate_dir)
        sharpness, wall_straightness = compute_map_quality_metrics(map_pgm)
        warning_hits = int(evaluator_data.get("tf_or_time_warning_hits", "0") or "0")
        warning_penalty = math.log1p(max(0, warning_hits))
        prior = prior_penalty(params, bootstrap.bootstrap_center)
        scan_score = scan_support_score(bag_summary) if use_scan_score else 0.0
        final_score = (
            END_SCORE_WEIGHTS["map_sharpness"] * normalize_metric(sharpness, 0.0, 150.0)
            + END_SCORE_WEIGHTS["wall_straightness"] * wall_straightness
            + END_SCORE_WEIGHTS["scan_support"] * scan_score
            - END_SCORE_WEIGHTS["warning_penalty"] * warning_penalty
            - END_SCORE_WEIGHTS["prior_penalty"] * prior
        )
        notes.append(
            json.dumps(
                {
                    "sharpness": sharpness,
                    "wall_straightness": wall_straightness,
                    "warning_hits": warning_hits,
                    "warning_penalty": warning_penalty,
                    "scan_support": scan_score,
                    "prior_penalty": prior,
                }
            )
        )
        return CandidateResult(
            params=params,
            stage_a_score=0.0,
            stage_b_score=final_score,
            final_score=final_score,
            run_dir=candidate_dir,
            status="ok",
            notes=notes,
        )
    finally:
        for proc in reversed(processes):
            terminate_process(proc)


def terminate_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5.0)


def normalize_metric(value: float, min_value: float, max_value: float) -> float:
    if max_value <= min_value:
        return 0.0
    clipped = max(min_value, min(max_value, value))
    return (clipped - min_value) / (max_value - min_value)


def write_bootstrap_summary(path: Path, bag_summary: BagSummary, bootstrap: BootstrapResult, bootstrap_seconds: float) -> None:
    yaml_mod = require_yaml_module()
    data = {
        "source_bag": str(bag_summary.path),
        "bootstrap_seconds": float(bootstrap_seconds),
        "bag_duration_sec": float(bag_summary.duration_sec),
        "camera_info_frame": bootstrap.camera_info_frame,
        "camera_link_frame": bootstrap.camera_link_frame,
        "bootstrap_success": bool(bootstrap.success),
        "frames_used": int(bootstrap.frames_used),
        "floor_frames": int(bootstrap.floor_frames),
        "wall_frames": int(bootstrap.wall_frames),
        "wall_floor_frames": int(bootstrap.wall_floor_frames),
        "floor_detected": bool(bootstrap.floor_detected),
        "wall_detected": bool(bootstrap.wall_detected),
        "estimated_roll_deg": bootstrap.estimated_roll_deg,
        "estimated_pitch_deg": bootstrap.estimated_pitch_deg,
        "estimated_yaw_deg": bootstrap.estimated_yaw_deg,
        "estimated_camera_height_m": bootstrap.estimated_camera_height_m,
        "bootstrap_center": bootstrap.bootstrap_center,
        "optical_to_camera_link_xyz": bootstrap.optical_to_camera_link_xyz,
        "optical_to_camera_link_rpy_deg": bootstrap.optical_to_camera_link_rpy_deg,
        "notes": bootstrap.notes,
        "frame_results": bootstrap.frame_results,
    }
    path.write_text(yaml_mod.safe_dump(data, sort_keys=False), encoding="utf-8")


def write_study_trials(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_best_files(
    run_dir: Path,
    bag_summary: BagSummary,
    bootstrap: BootstrapResult,
    best: CandidateResult,
) -> None:
    yaml_mod = require_yaml_module()
    best_yaml = run_dir / "best_extrinsics.yaml"
    best_env = run_dir / "best_extrinsics.env"
    payload = {
        "x": best.params["x"],
        "y": best.params["y"],
        "z": best.params["z"],
        "roll_deg": best.params["roll_deg"],
        "pitch_deg": best.params["pitch_deg"],
        "yaw_deg": best.params["yaw_deg"],
        "source_bag": str(bag_summary.path),
        "score": best.final_score,
        "bootstrap_success": bool(bootstrap.success),
        "camera_info_frame": bootstrap.camera_info_frame,
        "camera_link_frame": bootstrap.camera_link_frame,
        "optical_to_camera_link_xyz": bootstrap.optical_to_camera_link_xyz,
        "optical_to_camera_link_rpy_deg": bootstrap.optical_to_camera_link_rpy_deg,
    }
    best_yaml.write_text(yaml_mod.safe_dump(payload, sort_keys=False), encoding="utf-8")
    optical_xyz = (
        " ".join(str(v) for v in payload["optical_to_camera_link_xyz"])
        if payload["optical_to_camera_link_xyz"]
        else ""
    )
    optical_rpy = (
        " ".join(str(v) for v in payload["optical_to_camera_link_rpy_deg"])
        if payload["optical_to_camera_link_rpy_deg"]
        else ""
    )
    best_env.write_text(
        "\n".join(
            [
                f"X={shlex.quote(str(payload['x']))}",
                f"Y={shlex.quote(str(payload['y']))}",
                f"Z={shlex.quote(str(payload['z']))}",
                f"ROLL_DEG={shlex.quote(str(payload['roll_deg']))}",
                f"PITCH_DEG={shlex.quote(str(payload['pitch_deg']))}",
                f"YAW_DEG={shlex.quote(str(payload['yaw_deg']))}",
                f"SOURCE_BAG={shlex.quote(str(payload['source_bag']))}",
                f"SCORE={shlex.quote(str(payload['score']))}",
                f"BOOTSTRAP_SUCCESS={shlex.quote('true' if payload['bootstrap_success'] else 'false')}",
                f"CAMERA_INFO_FRAME={shlex.quote(payload['camera_info_frame'] or '')}",
                f"CAMERA_LINK_FRAME={shlex.quote(payload['camera_link_frame'] or '')}",
                f"OPTICAL_TO_CAMERA_LINK_XYZ={shlex.quote(optical_xyz)}",
                f"OPTICAL_TO_CAMERA_LINK_RPY_DEG={shlex.quote(optical_rpy)}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_report(
    path: Path,
    bag_summary: BagSummary,
    bootstrap: BootstrapResult,
    best: CandidateResult | None,
    args: argparse.Namespace,
    scan_found: bool,
    rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Camera Mount Calibration Report",
        "",
        f"- Source bag: `{bag_summary.path}`",
        f"- Bag duration: `{bag_summary.duration_sec:.2f}` s",
        f"- Bootstrap window: `{args.bootstrap_seconds}` s",
        f"- `/scan` found in latest bag: `{scan_found}`",
        f"- Bootstrap success: `{bootstrap.success}`",
        f"- Frames used for bootstrap: `{bootstrap.frames_used}`",
        f"- Floor frames: `{bootstrap.floor_frames}`",
        f"- Wall frames: `{bootstrap.wall_frames}`",
        f"- Wall+floor frames: `{bootstrap.wall_floor_frames}`",
        "",
        "## Search Space",
        "",
    ]
    for key, bounds in SEARCH_SPACE.items():
        lines.append(f"- `{key}` in `{bounds}`")
    lines += ["", "## Bootstrap", ""]
    if bootstrap.notes:
        for note in bootstrap.notes:
            lines.append(f"- {note}")
    lines += [
        f"- Estimated roll: `{bootstrap.estimated_roll_deg}`",
        f"- Estimated pitch: `{bootstrap.estimated_pitch_deg}`",
        f"- Estimated yaw: `{bootstrap.estimated_yaw_deg}`",
        f"- Estimated camera height: `{bootstrap.estimated_camera_height_m}`",
        "",
        "## Best Candidate",
        "",
    ]
    if best is None:
        lines.append("- No optimized candidate available.")
    else:
        for key, value in best.params.items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append(f"- Final score: `{best.final_score}`")
        lines.append(f"- Candidate status: `{best.status}`")
        if best.run_dir is not None:
            lines.append(f"- Candidate artifacts: `{best.run_dir}`")
    lines += ["", "## Trials", "", f"- Trial rows written: `{len(rows)}`", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def print_start_summary(
    bag_summary: BagSummary,
    args: argparse.Namespace,
    run_dir: Path,
    scan_found: bool,
) -> None:
    eprint(f"[camera_mount_calibration] Selected latest bag: {bag_summary.path}")
    eprint(f"[camera_mount_calibration] Bootstrap window: {args.bootstrap_seconds:.1f} s")
    eprint("[camera_mount_calibration] Search space:")
    for key, bounds in SEARCH_SPACE.items():
        eprint(f"  {key}: {bounds}")
    eprint(f"[camera_mount_calibration] /scan found in bag: {scan_found}")
    eprint(f"[camera_mount_calibration] Results directory: {run_dir}")


def main() -> int:
    args = parse_args()
    require_yaml_module()
    require_numeric_stack()
    bag_summary = newest_valid_bag(BAGS_ROOT)
    run_dir = make_output_dirs()
    scan_found = SCAN_TOPIC in bag_summary.topics
    print_start_summary(bag_summary, args, run_dir, scan_found)

    camera_model, frames, static_transforms = gather_bootstrap_data(bag_summary, args.bootstrap_seconds)
    bootstrap = build_bootstrap_result(camera_model, frames, static_transforms)
    write_bootstrap_summary(run_dir / "bootstrap_summary.yaml", bag_summary, bootstrap, args.bootstrap_seconds)

    rows: list[dict[str, Any]] = []
    best_candidate: CandidateResult | None = None

    if args.dry_run:
        write_study_trials(run_dir / "study_trials.csv", rows)
        write_report(
            run_dir / "calibration_report.md",
            bag_summary,
            bootstrap,
            None,
            args,
            scan_found,
            rows,
        )
        update_latest_symlink(run_dir)
        return 0

    optuna, TPESampler = require_optuna()
    optical_chain = None
    if bootstrap.camera_link_frame == "camera_link" and bootstrap.optical_to_camera_link_xyz is not None:
        optical_chain = (
            np.array(bootstrap.optical_to_camera_link_xyz, dtype=np.float64),
            Rotation.from_euler(
                "xyz", bootstrap.optical_to_camera_link_rpy_deg or (0.0, 0.0, 0.0), degrees=True
            ),
        )

    objective = make_fast_objective(frames, bootstrap, optical_chain)
    study = optuna.create_study(direction="maximize", sampler=TPESampler(seed=17))
    study.optimize(objective, n_trials=args.fast_trials)

    sorted_trials = sorted(
        [trial for trial in study.trials if trial.value is not None],
        key=lambda trial: float(trial.value),
        reverse=True,
    )
    top_trials = sorted_trials[: max(1, args.refine_trials)]
    candidate_results: list[CandidateResult] = []
    for index, trial in enumerate(top_trials, start=1):
        params = {
            key: float(trial.params[key])
            for key in ["x", "y", "z", "roll_deg", "pitch_deg", "yaw_deg"]
        }
        candidate = CandidateResult(
            params=params,
            stage_a_score=float(trial.value),
            stage_b_score=None,
            final_score=None,
            run_dir=None,
            status="stage_a_only",
            notes=[],
        )
        try:
            stage_b = run_stage_b_candidate(index, params, bag_summary, bootstrap, run_dir, args.use_scan_score)
            candidate.stage_b_score = stage_b.stage_b_score
            candidate.final_score = stage_b.final_score
            candidate.run_dir = stage_b.run_dir
            candidate.status = stage_b.status
            candidate.notes = stage_b.notes
        except Exception as exc:
            candidate.status = "stage_b_failed"
            candidate.notes = [str(exc)]
            candidate.final_score = -1e9
        candidate_results.append(candidate)

    for trial in sorted_trials:
        params = {key: trial.params.get(key) for key in ["x", "y", "z", "roll_deg", "pitch_deg", "yaw_deg"]}
        matching = next(
            (
                candidate
                for candidate in candidate_results
                if all(abs(candidate.params[key] - float(params[key])) < 1e-9 for key in candidate.params)
            ),
            None,
        )
        rows.append(
            {
                "trial_number": trial.number,
                **params,
                "stage_a_score": trial.value,
                "stage_b_score": matching.stage_b_score if matching else "",
                "final_score": matching.final_score if matching else "",
                "status": matching.status if matching else "stage_a_only",
                "notes": " | ".join(matching.notes) if matching else "",
            }
        )

    if candidate_results:
        best_candidate = max(candidate_results, key=lambda candidate: float(candidate.final_score or -1e9))
        if best_candidate.final_score is None or best_candidate.final_score <= -1e8:
            best_candidate = None

    write_study_trials(run_dir / "study_trials.csv", rows)
    if best_candidate is not None:
        write_best_files(run_dir, bag_summary, bootstrap, best_candidate)
    write_report(
        run_dir / "calibration_report.md",
        bag_summary,
        bootstrap,
        best_candidate,
        args,
        scan_found,
        rows,
    )
    update_latest_symlink(run_dir)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CalibrationError as exc:
        print(f"[camera_mount_calibration] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
