"""Cube grasp-pose semantics and symmetry canonicalization."""

from dataclasses import dataclass
import math
from typing import Optional, Sequence, Tuple


Vector3 = Tuple[float, float, float]
Quaternion = Tuple[float, float, float, float]


def _norm(vector: Vector3) -> float:
    return math.sqrt(sum(component * component for component in vector))


def normalize(vector: Vector3) -> Vector3:
    """Normalize a vector and reject zero length."""

    length = _norm(vector)
    if length == 0.0:
        raise ValueError("zero-length vector is not canonicalizable")
    return tuple(component / length for component in vector)


def _dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vector3, b: Vector3) -> Vector3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(vector: Vector3, scale: float) -> Vector3:
    return (vector[0] * scale, vector[1] * scale, vector[2] * scale)


def canonicalize_axis_mod_pi(axis: Vector3) -> Vector3:
    """Make an undirected axis deterministic so axis and -axis are equivalent."""

    unit = normalize(axis)
    snapped = tuple(0.0 if abs(component) < 1.0e-9 else component for component in unit)
    for component in unit:
        if abs(component) < 1.0e-9:
            continue
        if component < 0.0:
            return tuple(-value for value in snapped)
        break
    return snapped


def orthogonalize_axis_to_normal(normal: Vector3, axis: Vector3) -> Vector3:
    """Project the in-plane edge axis away from the face normal."""

    normal_unit = normalize(normal)
    axis_unit = normalize(axis)
    projection = _dot(axis_unit, normal_unit)
    tangent = tuple(axis_unit[index] - projection * normal_unit[index] for index in range(3))
    return canonicalize_axis_mod_pi(normalize(tangent))


def _basis_to_quaternion(x_axis: Vector3, y_axis: Vector3, z_axis: Vector3) -> Quaternion:
    """Convert an orthonormal basis to xyzw quaternion."""

    m00, m01, m02 = x_axis[0], y_axis[0], z_axis[0]
    m10, m11, m12 = x_axis[1], y_axis[1], z_axis[1]
    m20, m21, m22 = x_axis[2], y_axis[2], z_axis[2]
    trace = m00 + m11 + m22

    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * s
        qx = (m21 - m12) / s
        qy = (m02 - m20) / s
        qz = (m10 - m01) / s
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2.0
        qw = (m21 - m12) / s
        qx = 0.25 * s
        qy = (m01 + m10) / s
        qz = (m02 + m20) / s
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2.0
        qw = (m02 - m20) / s
        qx = (m01 + m10) / s
        qy = 0.25 * s
        qz = (m12 + m21) / s
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2.0
        qw = (m10 - m01) / s
        qx = (m02 + m20) / s
        qy = (m12 + m21) / s
        qz = 0.25 * s
    return (qx, qy, qz, qw)


@dataclass(frozen=True)
class CubeGraspEstimatorConfig:
    """Defensive plausibility bounds for PRECISE cube grasp geometry."""

    cube_edge_length_m: float
    min_valid_points: int = 24
    min_in_plane_span_m: float = 0.01
    max_in_plane_span_m: float = 0.09
    max_face_thickness_m: float = 0.02


@dataclass(frozen=True)
class CubeGraspDiagnostics:
    """Minimal diagnostics for tests and conservative publish decisions."""

    point_count: int
    span_primary_m: float
    span_secondary_m: float
    face_thickness_m: float


@dataclass(frozen=True)
class CubeGraspPose:
    """Greifer-relevante Würfellage mit Symmetriekanonisierung."""

    center_xyz: Vector3
    face_normal: Vector3
    edge_axis_mod_pi: Vector3
    source_frame: str

    def canonicalized(self) -> "CubeGraspPose":
        """Return a symmetry-canonicalized cube grasp pose."""

        normal = normalize(self.face_normal)
        edge_axis = orthogonalize_axis_to_normal(normal, self.edge_axis_mod_pi)
        return CubeGraspPose(
            center_xyz=self.center_xyz,
            face_normal=normal,
            edge_axis_mod_pi=edge_axis,
            source_frame=self.source_frame,
        )

    def orientation_xyzw(self) -> Quaternion:
        """Build a deterministic grasp-frame orientation from the canonical grasp cues."""

        normal = normalize(self.face_normal)
        x_axis = orthogonalize_axis_to_normal(normal, self.edge_axis_mod_pi)
        y_axis = normalize(_cross(normal, x_axis))
        return _basis_to_quaternion(x_axis, y_axis, normal)


def build_canonical_cube_grasp_pose(
    center_xyz: Vector3,
    face_normal: Vector3,
    edge_axis_mod_pi: Vector3,
    source_frame: str,
) -> CubeGraspPose:
    """Construct a canonical cube grasp pose from raw orientation cues."""

    return CubeGraspPose(
        center_xyz=center_xyz,
        face_normal=face_normal,
        edge_axis_mod_pi=edge_axis_mod_pi,
        source_frame=source_frame,
    ).canonicalized()


@dataclass(frozen=True)
class CubeGraspEstimate:
    """Estimated grasp pose plus conservative diagnostics."""

    grasp_pose: CubeGraspPose
    diagnostics: CubeGraspDiagnostics


def _project_span(points_xyz: Sequence[Vector3], axis: Vector3) -> float:
    values = [_dot(point, axis) for point in points_xyz]
    return max(values) - min(values)


def estimate_cube_grasp_pose(
    points_xyz: Sequence[Vector3],
    *,
    source_frame: str,
    config: CubeGraspEstimatorConfig,
    camera_origin_xyz: Vector3 = (0.0, 0.0, 0.0),
) -> Optional[CubeGraspEstimate]:
    """Estimate a conservative, symmetry-canonicalized cube grasp pose.

    This intentionally does not claim a unique cube identity. It uses the
    visible support cloud, the viewing direction, and deterministic tangent
    selection to produce a grasp-relevant frame only when the geometry is
    plausibly consistent with a cube face observation.
    """

    if len(points_xyz) < config.min_valid_points:
        return None

    face_centroid = tuple(sum(point[index] for point in points_xyz) / len(points_xyz) for index in range(3))
    view_vector = _sub(camera_origin_xyz, face_centroid)
    if _norm(view_vector) == 0.0:
        return None
    face_normal = normalize(view_vector)

    reference_axes = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    tangent_candidates = []
    for reference in reference_axes:
        try:
            tangent_candidates.append(orthogonalize_axis_to_normal(face_normal, reference))
        except ValueError:
            continue
    if not tangent_candidates:
        return None

    span_pairs = []
    for tangent in tangent_candidates:
        secondary = normalize(_cross(face_normal, tangent))
        span_pairs.append(
            (
                tangent,
                secondary,
                _project_span(points_xyz, tangent),
                _project_span(points_xyz, secondary),
                _project_span(points_xyz, face_normal),
            )
        )

    tangent, secondary, span_primary_m, span_secondary_m, face_thickness_m = max(
        span_pairs,
        key=lambda item: (item[2], item[3]),
    )
    if max(span_primary_m, span_secondary_m) < config.min_in_plane_span_m:
        return None
    if max(span_primary_m, span_secondary_m) > config.max_in_plane_span_m:
        return None
    if face_thickness_m > config.max_face_thickness_m:
        return None

    center_xyz = _sub(face_centroid, _scale(face_normal, config.cube_edge_length_m / 2.0))
    grasp_pose = build_canonical_cube_grasp_pose(
        center_xyz=center_xyz,
        face_normal=face_normal,
        edge_axis_mod_pi=tangent,
        source_frame=source_frame,
    )
    return CubeGraspEstimate(
        grasp_pose=grasp_pose,
        diagnostics=CubeGraspDiagnostics(
            point_count=len(points_xyz),
            span_primary_m=span_primary_m,
            span_secondary_m=span_secondary_m,
            face_thickness_m=face_thickness_m,
        ),
    )
