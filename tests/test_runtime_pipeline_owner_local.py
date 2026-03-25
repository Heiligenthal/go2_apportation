from src.go2_cube_perception.go2_cube_perception.depth_roi import BoundingBox2D, CameraIntrinsics
from src.go2_cube_perception.go2_cube_perception.object_detector_trt_node import (
    Detector2DCandidate,
    evaluate_detector_runtime_snapshot,
    select_best_candidate,
)
from src.go2_cube_perception.go2_cube_perception.object_position_fast_node import (
    FastProjectionConfig,
    build_fast_pipeline_outputs,
    evaluate_fast_runtime_snapshot,
)
from src.go2_object_tracking.go2_object_tracking.msg_adapters import InternalTrackingMeasurement
from src.go2_object_tracking.go2_object_tracking.map_filter import new_map_tracking_state
from src.go2_object_tracking.go2_object_tracking.object_tracker_node import (
    GeometricTargetHints,
    TrackingDecisionFlags,
    TrackerRuntimeState,
    advance_tracker_runtime,
    evaluate_tracker_input_snapshot,
)
from src.go2_object_tracking.go2_object_tracking.throw_logic import ThrowLogicState, ThrowStateMachine


def test_owner_local_detector_to_fast_to_tracker_flow_stays_consistent() -> None:
    candidate = Detector2DCandidate(
        bbox=BoundingBox2D(1, 1, 3, 3),
        confidence=0.91,
        frame_id="odom",
        stamp_s=10.0,
    )
    detector_snapshot = evaluate_detector_runtime_snapshot(
        now_s=10.1,
        candidate=candidate,
        rgb_stamp_s=10.0,
        camera_info_stamp_s=10.0,
        freshness_timeout_s=0.5,
        rgb_required=False,
        camera_info_required=False,
        rgb_topic="/camera/realsense2_camera/color/image_raw",
        camera_info_topic="/camera/realsense2_camera/color/camera_info",
        internal_candidate_topic="/perception/internal/cube_bbox",
        object_visible_topic="/perception/object_visible",
        look_outputs_enabled=False,
    )
    assert select_best_candidate([candidate], confidence_threshold=0.39) is not None
    fast_snapshot = evaluate_fast_runtime_snapshot(
        now_s=10.1,
        candidate_stamp_s=10.0,
        depth_stamp_s=10.0,
        intrinsics_stamp_s=10.0,
        freshness_timeout_s=0.5,
        candidate_topic="/perception/internal/cube_bbox",
        depth_topic="/camera/realsense2_camera/aligned_depth_to_color/image_raw",
        camera_info_topic="/camera/realsense2_camera/color/camera_info",
        map_tf_ready=True,
    )
    outputs = build_fast_pipeline_outputs(
        candidate,
        depth_image=[
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 2.0, 2.0, 0.0],
            [0.0, 2.0, 2.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ],
        intrinsics=CameraIntrinsics(fx=2.0, fy=2.0, cx=0.0, cy=0.0),
        config=FastProjectionConfig(
            output_frame="odom",
            min_depth_m=0.4,
            max_depth_m=5.0,
            min_valid_pixels=4,
            trim_ratio=0.1,
        ),
        transform_point_to_map=lambda point_xyz, source_frame_id, stamp_s: (
            point_xyz[0] + 1.0,
            point_xyz[1] + 2.0,
            point_xyz[2],
        ),
    )
    tracker_state = advance_tracker_runtime(
        TrackerRuntimeState(
            visibility_state="lost",
            last_measurement=None,
            last_map_measurement=None,
            map_state=new_map_tracking_state(),
            throw_state=ThrowLogicState(),
            measurement_age_s=float("inf"),
            decision_flags=TrackingDecisionFlags(False, False, True, False, False, False),
            geometric_targets=GeometricTargetHints(None, None, None, False),
        ),
        now_s=10.1,
        incoming_measurement=InternalTrackingMeasurement(
            frame_id=outputs.public_detection.frame_id if outputs.public_detection is not None else "odom",
            center_xyz=outputs.public_detection.center_xyz if outputs.public_detection is not None else (0.0, 0.0, 0.0),
            confidence=outputs.public_detection.confidence if outputs.public_detection is not None else 0.0,
            stamp_s=outputs.public_detection.stamp_s if outputs.public_detection is not None else 0.0,
        ),
        incoming_map_measurement=outputs.map_measurement,
        visible_timeout_s=0.2,
        occlusion_timeout_s=0.6,
        verify_timeout_s=1.5,
        throw_state_machine=ThrowStateMachine(release_speed_threshold_mps=1.0, confirm_measurements=3),
        min_update_confidence=0.39,
        short_occlusion_timeout_s=1.0,
        local_search_probability_threshold=0.05,
        pick_ready_min_probability=0.40,
        pick_ready_max_speed_mps=0.15,
        precise_pose_available=False,
        precise_pose_age_s=None,
        pick_ready_max_precise_age_s=0.5,
        reposition_requested=False,
        robot_map_position_xyz=(0.0, 0.0, 0.0),
        safety_distance_min_m=1.5,
        safety_distance_max_m=2.0,
    )
    tracker_snapshot = evaluate_tracker_input_snapshot(
        input_mode="public_detection3d_array",
        public_input_topic="/tracking/detections3d_fast",
        candidate_input_topic="/tracking/internal/detections3d_fast_candidate",
        map_input_topic="/tracking/internal/cube_measurement_map",
        last_measurement=tracker_state.last_measurement,
        last_map_measurement=tracker_state.last_map_measurement,
        now_s=10.1,
        visible_timeout_s=0.2,
    )

    assert detector_snapshot.can_publish_visible is True
    assert fast_snapshot.can_project is True
    assert outputs.public_detection is not None
    assert outputs.map_measurement is not None
    assert tracker_state.visibility_state == "visible"
    assert tracker_snapshot.measurement_ready is True
    assert tracker_snapshot.map_measurement_ready is True
    assert tracker_state.map_state.frame_id == "map"
