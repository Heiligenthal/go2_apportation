from __future__ import annotations

from pathlib import Path

from src.go2_person_perception.go2_person_perception.contracts import (
    LOCAL_PERSON_POSE_INPUT_TOPIC,
    LOCAL_PERSON_VISIBLE_INPUT_TOPIC,
    PERSON_LAST_SEEN_TOPIC,
    PERSON_POSE_FRAME,
    PERSON_POSE_TOPIC,
    PERSON_VISIBLE_TOPIC,
)
from src.go2_person_perception.go2_person_perception.person_surface_logic import (
    LocalPoseInput,
    decide_pose_input,
    decide_visible_input,
)


def test_person_topic_names_match_freeze() -> None:
    assert PERSON_VISIBLE_TOPIC == "/perception/person_visible"
    assert PERSON_POSE_TOPIC == "/perception/person_pose"
    assert PERSON_LAST_SEEN_TOPIC == "/perception/person_last_seen"
    assert LOCAL_PERSON_POSE_INPUT_TOPIC == "~/input/person_pose_map"
    assert LOCAL_PERSON_VISIBLE_INPUT_TOPIC == "~/input/person_visible"


def test_person_last_seen_updates_only_for_valid_map_pose() -> None:
    valid = decide_pose_input(LocalPoseInput(frame_id="map"), previous_visible=False)
    invalid = decide_pose_input(LocalPoseInput(frame_id="odom"), previous_visible=False)
    missing = decide_pose_input(None, previous_visible=False)

    assert valid.publish_pose is True
    assert valid.publish_last_seen is True
    assert valid.last_seen_frame_id == "map"

    assert invalid.publish_pose is False
    assert invalid.publish_last_seen is False

    assert missing.publish_pose is False
    assert missing.publish_last_seen is False


def test_visibility_input_changes_visible_without_inventing_pose() -> None:
    decision = decide_visible_input(False)

    assert decision.visible is False
    assert decision.publish_pose is False
    assert decision.publish_last_seen is False


def test_person_pose_outputs_use_map_frame_in_node_source() -> None:
    node_source = Path(
        "src/go2_person_perception/go2_person_perception/person_surface_node.py"
    ).read_text(encoding="utf-8")

    assert 'normalized_pose.header.frame_id = PERSON_POSE_FRAME' in node_source
    assert PERSON_POSE_FRAME == "map"


def test_person_surface_node_uses_frozen_message_types_and_no_control_path() -> None:
    node_source = Path(
        "src/go2_person_perception/go2_person_perception/person_surface_node.py"
    ).read_text(encoding="utf-8")

    assert "create_publisher(Bool, PERSON_VISIBLE_TOPIC" in node_source
    assert "create_publisher(PoseStamped, PERSON_POSE_TOPIC" in node_source
    assert "create_publisher(PoseStamped, PERSON_LAST_SEEN_TOPIC" in node_source
    assert "LOCAL_PERSON_POSE_INPUT_TOPIC" in node_source
    assert "LOCAL_PERSON_VISIBLE_INPUT_TOPIC" in node_source
    assert "cmd_vel" not in node_source
