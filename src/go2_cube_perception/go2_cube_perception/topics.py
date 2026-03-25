"""Topic constants for cube perception.

These values are a thin owner-local convenience mirror of the current
runtime/shared-surface handoff. They intentionally do not replace
``config/contracts.yaml`` or ``config/runtime_topics.yaml``.
"""

RGB_IMAGE = "/camera/realsense2_camera/color/image_raw"
DEPTH_IMAGE = "/camera/realsense2_camera/aligned_depth_to_color/image_raw"
CAMERA_INFO = "/camera/realsense2_camera/color/camera_info"
PRIMARY_RUNTIME_SENSOR_TOPICS = (
    RGB_IMAGE,
    DEPTH_IMAGE,
    CAMERA_INFO,
)

OBJECT_VISIBLE = "/perception/object_visible"
OBJECT_POSE_6D = "/perception/object_pose_6d"
OBJECT_LAST_SEEN = "/perception/object_last_seen"
DETECTIONS3D_FAST = "/tracking/detections3d_fast"

INTERNAL_CUBE_BBOX = "/perception/internal/cube_bbox"
INTERNAL_FAST_CANDIDATE = "/tracking/internal/detections3d_fast_candidate"
INTERNAL_MAP_MEASUREMENT = "/tracking/internal/cube_measurement_map"
INTERNAL_PRECISE_CANDIDATE = "/perception/internal/cube_pose_candidate"
LOOK_YAW_DELTA = "/look_yaw_delta"
BALANCE_RPY_CMD = "/balance_rpy_cmd"
OWNER_LOCAL_PIPELINE_TOPICS = (
    INTERNAL_CUBE_BBOX,
    INTERNAL_FAST_CANDIDATE,
    INTERNAL_MAP_MEASUREMENT,
    INTERNAL_PRECISE_CANDIDATE,
)

PUBLIC_SAFE_OUTPUT_TOPICS = (
    OBJECT_VISIBLE,
    OBJECT_POSE_6D,
    OBJECT_LAST_SEEN,
    DETECTIONS3D_FAST,
)
READY_PUBLIC_OUTPUT_TOPICS = PUBLIC_SAFE_OUTPUT_TOPICS
BLOCKED_BY_H06_OUTPUT_TOPICS = ()
PUBLIC_WIRE_TYPES = {
    OBJECT_VISIBLE: "std_msgs/Bool",
    OBJECT_POSE_6D: "geometry_msgs/PoseStamped",
    OBJECT_LAST_SEEN: "geometry_msgs/PoseStamped",
    DETECTIONS3D_FAST: "go2_apportation_msgs/Detection3DArray",
}
INTERNAL_OUTPUT_TOPICS = (
    INTERNAL_CUBE_BBOX,
    INTERNAL_FAST_CANDIDATE,
    INTERNAL_MAP_MEASUREMENT,
    INTERNAL_PRECISE_CANDIDATE,
)
