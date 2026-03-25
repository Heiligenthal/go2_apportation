"""Depth ROI helpers for FAST/PRECISE skeletons."""

from dataclasses import dataclass
from math import isfinite
from statistics import median
from typing import List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class BoundingBox2D:
    """Pixel-space bounding box."""

    x_min: int
    y_min: int
    x_max: int
    y_max: int

    @property
    def width(self) -> int:
        return max(0, self.x_max - self.x_min)

    @property
    def height(self) -> int:
        return max(0, self.y_max - self.y_min)

    def clamped(self, image_width: int, image_height: int) -> "BoundingBox2D":
        """Clamp the ROI to image bounds."""

        return BoundingBox2D(
            x_min=max(0, min(self.x_min, image_width)),
            y_min=max(0, min(self.y_min, image_height)),
            x_max=max(0, min(self.x_max, image_width)),
            y_max=max(0, min(self.y_max, image_height)),
        )

    @property
    def center_u(self) -> float:
        return float(self.x_min + self.x_max) / 2.0

    @property
    def center_v(self) -> float:
        return float(self.y_min + self.y_max) / 2.0


@dataclass(frozen=True)
class CameraIntrinsics:
    """Minimal pinhole intrinsics for FAST projection."""

    fx: float
    fy: float
    cx: float
    cy: float


@dataclass(frozen=True)
class DepthRoiConfig:
    """Configurable, small but real ROI depth summary settings."""

    min_depth_m: float
    max_depth_m: float
    min_valid_pixels: int = 8
    trim_ratio: float = 0.1
    center_weight_multiplier: int = 3


@dataclass(frozen=True)
class DepthRoiSummary:
    """Robust scalar summary and lightweight diagnostics for a depth ROI."""

    depth_m: float
    valid_pixel_count: int
    roi_pixel_count: int
    weighted_sample_count: int
    statistic: str


Point3D = Tuple[float, float, float]


@dataclass(frozen=True)
class PointCloudExtractionConfig:
    """Small but real configuration for PRECISE local point extraction."""

    min_depth_m: float
    max_depth_m: float
    min_valid_points: int = 24
    max_depth_deviation_m: float = 0.03
    max_axis_aligned_extent_m: float = 0.12


@dataclass(frozen=True)
class LocalPointCloud:
    """Owner-local 3D support cloud extracted from depth and ROI."""

    points_xyz: Tuple[Point3D, ...]
    median_depth_m: float
    valid_point_count: int
    bbox: BoundingBox2D


def valid_depth_samples(depth_values: List[float], min_depth_m: float, max_depth_m: float) -> List[float]:
    """Filter a flattened ROI to the supported depth band."""

    return [
        value
        for value in depth_values
        if isfinite(value) and min_depth_m <= value <= max_depth_m
    ]


def _trimmed_samples(depth_values: List[float], trim_ratio: float) -> List[float]:
    """Trim extremes without collapsing the whole sample set."""

    if not depth_values:
        return []
    bounded_ratio = max(0.0, min(trim_ratio, 0.45))
    trim_count = int(len(depth_values) * bounded_ratio)
    if trim_count <= 0 or (2 * trim_count) >= len(depth_values):
        return list(depth_values)
    return depth_values[trim_count:-trim_count]


def _center_weighted_valid_samples(
    depth_image: Sequence[Sequence[float]],
    bbox: BoundingBox2D,
    config: DepthRoiConfig,
) -> Optional[DepthRoiSummary]:
    """Collect valid samples and emphasize the ROI center for robustness."""

    if not depth_image or not depth_image[0]:
        return None

    clamped_bbox = bbox.clamped(image_width=len(depth_image[0]), image_height=len(depth_image))
    if clamped_bbox.width <= 0 or clamped_bbox.height <= 0:
        return None

    center_x_min = clamped_bbox.x_min + max(1, clamped_bbox.width // 4)
    center_x_max = clamped_bbox.x_max - max(1, clamped_bbox.width // 4)
    center_y_min = clamped_bbox.y_min + max(1, clamped_bbox.height // 4)
    center_y_max = clamped_bbox.y_max - max(1, clamped_bbox.height // 4)

    valid_samples: List[float] = []
    valid_pixel_count = 0
    roi_pixel_count = clamped_bbox.width * clamped_bbox.height

    for v in range(clamped_bbox.y_min, clamped_bbox.y_max):
        row = depth_image[v]
        for u in range(clamped_bbox.x_min, clamped_bbox.x_max):
            value = row[u]
            if not isfinite(value) or value < config.min_depth_m or value > config.max_depth_m:
                continue
            valid_pixel_count += 1
            center_weight = (
                config.center_weight_multiplier
                if center_x_min <= u < center_x_max and center_y_min <= v < center_y_max
                else 1
            )
            valid_samples.extend([float(value)] * max(1, center_weight))

    if valid_pixel_count < config.min_valid_pixels or not valid_samples:
        return None

    trimmed = _trimmed_samples(sorted(valid_samples), trim_ratio=config.trim_ratio)
    if not trimmed:
        return None

    return DepthRoiSummary(
        depth_m=float(median(trimmed)),
        valid_pixel_count=valid_pixel_count,
        roi_pixel_count=roi_pixel_count,
        weighted_sample_count=len(trimmed),
        statistic="center_weighted_trimmed_median",
    )


def summarize_depth_roi(
    depth_values: List[float],
    min_depth_m: float,
    max_depth_m: float,
) -> Optional[float]:
    """Return a robust scalar summary for a depth ROI."""

    filtered = valid_depth_samples(depth_values, min_depth_m=min_depth_m, max_depth_m=max_depth_m)
    if not filtered:
        return None
    return float(median(filtered))


def summarize_depth_bbox(
    depth_image: Sequence[Sequence[float]],
    bbox: BoundingBox2D,
    config: DepthRoiConfig,
) -> Optional[DepthRoiSummary]:
    """Summarize a 2D depth ROI with light robustness and validity gating."""

    return _center_weighted_valid_samples(depth_image, bbox=bbox, config=config)


def _axis_aligned_extent(points_xyz: Sequence[Point3D]) -> float:
    """Return the maximum axis-aligned extent across x/y/z."""

    if not points_xyz:
        return 0.0
    spans = []
    for axis in range(3):
        values = [point[axis] for point in points_xyz]
        spans.append(max(values) - min(values))
    return max(spans)


def extract_local_point_cloud(
    depth_image: Sequence[Sequence[float]],
    bbox: BoundingBox2D,
    intrinsics: CameraIntrinsics,
    config: PointCloudExtractionConfig,
    support_mask: Optional[Sequence[Sequence[bool]]] = None,
) -> Optional[LocalPointCloud]:
    """Extract a local 3D support cloud from ROI depth, optionally masked."""

    if not depth_image or not depth_image[0]:
        return None

    clamped_bbox = bbox.clamped(image_width=len(depth_image[0]), image_height=len(depth_image))
    if clamped_bbox.width <= 0 or clamped_bbox.height <= 0:
        return None

    valid_depths: List[Tuple[int, int, float]] = []
    for v in range(clamped_bbox.y_min, clamped_bbox.y_max):
        row = depth_image[v]
        for u in range(clamped_bbox.x_min, clamped_bbox.x_max):
            if support_mask is not None and not bool(support_mask[v][u]):
                continue
            value = float(row[u])
            if not isfinite(value) or value < config.min_depth_m or value > config.max_depth_m:
                continue
            valid_depths.append((u, v, value))

    if len(valid_depths) < config.min_valid_points:
        return None

    median_depth_m = float(median([item[2] for item in valid_depths]))
    inliers = [
        item
        for item in valid_depths
        if abs(item[2] - median_depth_m) <= config.max_depth_deviation_m
    ]
    if len(inliers) < config.min_valid_points:
        return None

    points_xyz: List[Point3D] = []
    for u, v, z in inliers:
        x = ((float(u) - intrinsics.cx) * z) / intrinsics.fx
        y = ((float(v) - intrinsics.cy) * z) / intrinsics.fy
        points_xyz.append((x, y, z))

    if _axis_aligned_extent(points_xyz) > config.max_axis_aligned_extent_m:
        return None

    return LocalPointCloud(
        points_xyz=tuple(points_xyz),
        median_depth_m=median_depth_m,
        valid_point_count=len(points_xyz),
        bbox=clamped_bbox,
    )
