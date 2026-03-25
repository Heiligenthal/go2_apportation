#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WARNING_PATTERNS = (
    re.compile(r"TF_OLD_DATA", re.IGNORECASE),
    re.compile(r"extrapolat", re.IGNORECASE),
    re.compile(r"timestamp", re.IGNORECASE),
    re.compile(r"did not receive data since 5 seconds", re.IGNORECASE),
    re.compile(r"time difference between rgb and depth frames is high", re.IGNORECASE),
    re.compile(r"incompatible qos", re.IGNORECASE),
    re.compile(r"could not transform", re.IGNORECASE),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate exported RTAB-Map map artifacts and scan logs for TF/timing issues."
    )
    parser.add_argument("--map-dir", required=True, help="Path to artifacts/maps/<timestamp>")
    parser.add_argument(
        "--run-dir",
        help="Path to artifacts/r3_mapping/<timestamp> or another mapping run dir with logs",
    )
    parser.add_argument("--compare-map-dir", help="Optional baseline/comparison map dir")
    parser.add_argument("--compare-run-dir", help="Optional baseline/comparison run dir")
    return parser.parse_args()


def load_manifest(map_dir: Path) -> dict[str, str]:
    manifest = map_dir / "manifest.txt"
    data: dict[str, str] = {}
    if not manifest.exists():
        return data
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def parse_pgm_header(path: Path) -> tuple[int, int, int, int]:
    with path.open("rb") as fh:
        magic = fh.readline().strip()
        if magic not in {b"P5", b"P2"}:
            raise ValueError(f"Unsupported PGM magic: {magic!r}")

        def next_token() -> bytes:
            while True:
                line = fh.readline()
                if not line:
                    raise ValueError("Unexpected EOF in PGM header")
                line = line.strip()
                if not line or line.startswith(b"#"):
                    continue
                return line

        dims = next_token().split()
        if len(dims) != 2:
            raise ValueError("Invalid PGM width/height line")
        width = int(dims[0])
        height = int(dims[1])
        maxval = int(next_token())
        data = fh.read()
        expected = width * height
        if magic == b"P2":
            values = [int(token) for token in data.split()]
            if len(values) != expected:
                raise ValueError("ASCII PGM pixel count mismatch")
            pixels = values
        else:
            if maxval > 255:
                raise ValueError("16-bit PGM not supported by this evaluator")
            if len(data) < expected:
                raise ValueError("Binary PGM pixel count mismatch")
            pixels = list(data[:expected])
        return width, height, maxval, len(pixels), pixels


def scan_warning_counts(run_dir: Path | None) -> tuple[int, int]:
    if run_dir is None or not run_dir.exists():
        return 0, 0
    hits = 0
    files_with_hits = 0
    for path in sorted(run_dir.rglob("*.log")) + sorted(run_dir.rglob("*.out")) + sorted(
        run_dir.rglob("*.err")
    ):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        file_hit = False
        for line in text.splitlines():
            if any(pattern.search(line) for pattern in WARNING_PATTERNS):
                hits += 1
                file_hit = True
        if file_hit:
            files_with_hits += 1
    return hits, files_with_hits


def evaluate(map_dir: Path, run_dir: Path | None) -> dict[str, object]:
    manifest = load_manifest(map_dir)
    pgm_path = map_dir / "map.pgm"
    yaml_path = map_dir / "map.yaml"
    result: dict[str, object] = {
        "map_dir": str(map_dir),
        "run_dir": str(run_dir) if run_dir else "",
        "map_pgm_exists": pgm_path.exists(),
        "map_yaml_exists": yaml_path.exists(),
        "map_pgm_size_bytes": pgm_path.stat().st_size if pgm_path.exists() else 0,
        "extrinsics_profile": manifest.get("extrinsics_profile", ""),
        "camera_tf_source": manifest.get("camera_tf_source", ""),
        "camera_xyz": manifest.get("camera_xyz", ""),
        "camera_rpy": manifest.get("camera_rpy", ""),
        "lidar_xyz": manifest.get("lidar_xyz", ""),
        "lidar_rpy": manifest.get("lidar_rpy", ""),
    }

    if pgm_path.exists():
        width, height, maxval, pixel_count, pixels = parse_pgm_header(pgm_path)
        black_pixels = sum(1 for value in pixels if value <= 5)
        dark_pixels = sum(1 for value in pixels if value <= max(5, int(maxval * 0.10)))
        white_pixels = sum(1 for value in pixels if value >= maxval - 5)
        nonwhite_pixels = pixel_count - white_pixels
        result.update(
            {
                "map_width": width,
                "map_height": height,
                "map_maxval": maxval,
                "pixel_count": pixel_count,
                "pixel_min": min(pixels),
                "pixel_max": max(pixels),
                "black_ratio": round(black_pixels / pixel_count, 6),
                "dark_ratio": round(dark_pixels / pixel_count, 6),
                "white_ratio": round(white_pixels / pixel_count, 6),
                "nonwhite_ratio": round(nonwhite_pixels / pixel_count, 6),
            }
        )
        result["map_not_almost_empty"] = nonwhite_pixels / pixel_count >= 0.01
        result["map_not_almost_black"] = dark_pixels / pixel_count <= 0.95
    else:
        result["map_not_almost_empty"] = False
        result["map_not_almost_black"] = False

    warning_hits, warning_files = scan_warning_counts(run_dir)
    result["tf_or_time_warning_hits"] = warning_hits
    result["tf_or_time_warning_files"] = warning_files
    result["basic_acceptance_pass"] = bool(
        result["map_pgm_exists"]
        and result["map_yaml_exists"]
        and result["map_not_almost_empty"]
        and result["map_not_almost_black"]
    )
    return result


def classify(current: dict[str, object], other: dict[str, object]) -> str:
    current_pass = bool(current.get("basic_acceptance_pass"))
    other_pass = bool(other.get("basic_acceptance_pass"))
    current_nonwhite = float(current.get("nonwhite_ratio", 0.0))
    other_nonwhite = float(other.get("nonwhite_ratio", 0.0))
    current_warn = int(current.get("tf_or_time_warning_hits", 0))
    other_warn = int(other.get("tf_or_time_warning_hits", 0))

    if current_pass and not other_pass:
        return "better"
    if other_pass and not current_pass:
        return "worse"

    if current_nonwhite > other_nonwhite * 1.20 and current_warn <= other_warn:
        return "better"
    if other_nonwhite > current_nonwhite * 1.20 and other_warn <= current_warn:
        return "worse"

    if current_warn + 5 < other_warn and current_nonwhite >= other_nonwhite * 0.9:
        return "better"
    if other_warn + 5 < current_warn and other_nonwhite >= current_nonwhite * 0.9:
        return "worse"

    return "equal"


def emit(prefix: str, data: dict[str, object]) -> None:
    for key, value in data.items():
        if isinstance(value, bool):
            print(f"{prefix}{key}={'true' if value else 'false'}")
        else:
            print(f"{prefix}{key}={value}")


def main() -> int:
    args = parse_args()

    map_dir = Path(args.map_dir).resolve()
    run_dir = Path(args.run_dir).resolve() if args.run_dir else None
    current = evaluate(map_dir, run_dir)
    emit("", current)

    if args.compare_map_dir:
        compare_map_dir = Path(args.compare_map_dir).resolve()
        compare_run_dir = Path(args.compare_run_dir).resolve() if args.compare_run_dir else None
        other = evaluate(compare_map_dir, compare_run_dir)
        emit("compare_", other)
        print(f"comparison_result={classify(current, other)}")

    print("evaluation_json=" + json.dumps(current, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
