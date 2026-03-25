from pathlib import Path


PARAM_FILE = Path("/home/unitree/go2_apportation/src/go2_cube_perception/config/cube_perception.params.yaml")


def test_cube_perception_params_file_contains_required_scaffold() -> None:
    text = PARAM_FILE.read_text(encoding="utf-8")
    assert "cube_edge_length_m: 0.05" in text
    assert 'backend_kind: "tensorrt_stub"' in text
    assert 'backend_kind: "segmentation_depth_stub"' in text
    assert "input_width: 640" in text
    assert "confidence_threshold: 0.39" in text
    assert "input_freshness_timeout_s: 0.5" in text
    assert 'ingest_mode: "owner_local_candidate"' in text
    assert 'rgb_topic: "/camera/realsense2_camera/color/image_raw"' in text
    assert 'depth_topic: "/camera/realsense2_camera/aligned_depth_to_color/image_raw"' in text
    assert 'camera_info_topic: "/camera/realsense2_camera/color/camera_info"' in text
    assert "depth_min_valid_pixels: 8" in text
    assert "depth_trim_ratio: 0.1" in text
    assert 'internal_map_measurement_topic: "/tracking/internal/cube_measurement_map"' in text
    assert 'look_yaw_topic: "/look_yaw_delta"' in text
    assert 'balance_rpy_topic: "/balance_rpy_cmd"' in text
    assert 'map_tracking_frame: "map"' in text
    assert "min_valid_points: 24" in text
    assert "max_depth_deviation_m: 0.03" in text
    assert "max_face_thickness_m: 0.02" in text
    assert "enable_tf_last_seen_lookup: true" in text
    assert "last_seen_transform_timeout_s: 0.05" in text
    assert 'segmentation_engine_path: ""' in text
    assert 'detections3d_fast_wire_type: "go2_apportation_msgs/Detection3DArray"' in text
    assert 'object_pose_wire_type: "geometry_msgs/PoseStamped"' in text
    assert 'object_last_seen_wire_type: "geometry_msgs/PoseStamped"' in text
    assert 'object_last_seen_frame: "map"' in text


def test_cube_perception_params_keep_outputs_safe_by_default() -> None:
    text = PARAM_FILE.read_text(encoding="utf-8")
    assert "enabled: false" in text
    assert 'output_mode: "public_detection3d_array"' in text
    assert "allow_frame_passthrough_if_no_tf: false" in text
    assert "publish_bridge_look_outputs: false" in text
