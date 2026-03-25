from src.go2_cube_perception.go2_cube_perception import contracts as cube_contracts
from src.go2_cube_perception.go2_cube_perception import topics as cube_topics
from src.go2_object_tracking.go2_object_tracking.contracts import DEFAULT_CONTRACTS as tracking_contracts


def test_object_pose_and_last_seen_are_ready_pose_stamped_outputs() -> None:
    assert cube_contracts.DEFAULT_CONTRACTS.object_pose_topic == cube_topics.OBJECT_POSE_6D
    assert cube_contracts.DEFAULT_CONTRACTS.object_pose_wire_type == "geometry_msgs/PoseStamped"
    assert cube_contracts.DEFAULT_CONTRACTS.object_last_seen_topic == cube_topics.OBJECT_LAST_SEEN
    assert cube_contracts.DEFAULT_CONTRACTS.object_last_seen_wire_type == "geometry_msgs/PoseStamped"
    assert cube_contracts.DEFAULT_CONTRACTS.last_seen_output_frame == "map"


def test_detections3d_fast_is_ready_detection3darray_surface() -> None:
    assert cube_contracts.DEFAULT_CONTRACTS.detections3d_fast_topic == cube_topics.DETECTIONS3D_FAST
    assert cube_contracts.DEFAULT_CONTRACTS.detections3d_fast_wire_type == "go2_apportation_msgs/Detection3DArray"
    assert tracking_contracts.fast_input_topic == "/tracking/detections3d_fast"
    assert tracking_contracts.fast_input_wire_type == "go2_apportation_msgs/Detection3DArray"
    assert tracking_contracts.object_state_topic == "/tracking/object_state"
    assert tracking_contracts.object_state_wire_type == "go2_apportation_msgs/ObjectState"
    assert tracking_contracts.throw_status_topic == "/tracking/throw_status"
    assert tracking_contracts.throw_status_wire_type == "go2_apportation_msgs/ThrowStatus"
    assert tracking_contracts.predicted_region_topic == "/tracking/predicted_region"
    assert tracking_contracts.predicted_region_wire_type == "go2_apportation_msgs/PredictedRegion"
    assert tracking_contracts.intercept_goal_topic == "/tracking/intercept_goal"
    assert tracking_contracts.intercept_goal_wire_type == "go2_apportation_msgs/InterceptGoal"
    assert tracking_contracts.state_frame == "odom"
    assert tracking_contracts.internal_tracking_frame == "map"


def test_predicted_region_and_intercept_goal_are_tracking_public_outputs_only() -> None:
    assert "/tracking/predicted_region" not in cube_topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert "/tracking/intercept_goal" not in cube_topics.PUBLIC_SAFE_OUTPUT_TOPICS
    assert "/tracking/predicted_region" in tracking_contracts.public_safe_topics
    assert "/tracking/intercept_goal" in tracking_contracts.public_safe_topics
