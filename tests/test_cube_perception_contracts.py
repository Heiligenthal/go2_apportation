from pathlib import Path

from src.go2_cube_perception.go2_cube_perception import contracts, topics


def test_cube_contracts_match_project_context() -> None:
    assert contracts.DEFAULT_CONTRACTS.cube_edge_length_m == 0.05
    assert contracts.DEFAULT_CONTRACTS.gpu_first_required is True
    assert contracts.DEFAULT_CONTRACTS.color_search_enabled is False
    assert contracts.DEFAULT_CONTRACTS.marker_usage_enabled is False
    assert contracts.DEFAULT_CONTRACTS.active_object_count == 1
    assert contracts.DEFAULT_CONTRACTS.best_detection_confidence_threshold == 0.39
    assert contracts.DEFAULT_CONTRACTS.object_pose_wire_type == "geometry_msgs/PoseStamped"
    assert contracts.DEFAULT_CONTRACTS.object_last_seen_wire_type == "geometry_msgs/PoseStamped"
    assert contracts.DEFAULT_CONTRACTS.detections3d_fast_wire_type == "go2_apportation_msgs/Detection3DArray"
    assert contracts.DEFAULT_CONTRACTS.last_seen_output_frame == "map"
    assert contracts.DEFAULT_CONTRACTS.internal_tracking_frame == "map"
    assert contracts.DEFAULT_CONTRACTS.blocked_by_h06_topics == ()


def test_cube_public_outputs_exclude_blocked_and_motion_topics() -> None:
    assert topics.OBJECT_VISIBLE in topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert topics.OBJECT_POSE_6D in topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert topics.OBJECT_LAST_SEEN in topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert topics.DETECTIONS3D_FAST in topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert "/cmd_vel" not in topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert "/cmd_vel" not in topics.BLOCKED_BY_H06_OUTPUT_TOPICS
    assert topics.INTERNAL_CUBE_BBOX in topics.OWNER_LOCAL_PIPELINE_TOPICS
    assert topics.INTERNAL_FAST_CANDIDATE in topics.OWNER_LOCAL_PIPELINE_TOPICS
    assert topics.INTERNAL_MAP_MEASUREMENT in topics.OWNER_LOCAL_PIPELINE_TOPICS
    assert topics.INTERNAL_PRECISE_CANDIDATE in topics.OWNER_LOCAL_PIPELINE_TOPICS
    assert topics.LOOK_YAW_DELTA == "/look_yaw_delta"
    assert topics.BALANCE_RPY_CMD == "/balance_rpy_cmd"


def test_cube_sensor_topic_defaults_match_h1_runtime_handoff() -> None:
    assert topics.RGB_IMAGE == "/camera/realsense2_camera/color/image_raw"
    assert topics.DEPTH_IMAGE == "/camera/realsense2_camera/aligned_depth_to_color/image_raw"
    assert topics.CAMERA_INFO == "/camera/realsense2_camera/color/camera_info"
    assert topics.PRIMARY_RUNTIME_SENSOR_TOPICS == (
        topics.RGB_IMAGE,
        topics.DEPTH_IMAGE,
        topics.CAMERA_INFO,
    )


def test_cube_perception_sources_do_not_reference_cmd_vel() -> None:
    package_root = Path("/home/unitree/go2_apportation/src/go2_cube_perception")
    for source_file in package_root.rglob("*.py"):
        assert "cmd_vel" not in source_file.read_text(encoding="utf-8")
