from __future__ import annotations

from dataclasses import dataclass

from .contracts import PERSON_POSE_FRAME


@dataclass(frozen=True)
class LocalPoseInput:
    frame_id: str


@dataclass(frozen=True)
class PersonSurfaceDecision:
    visible: bool
    publish_pose: bool
    publish_last_seen: bool
    pose_frame_id: str | None = None
    last_seen_frame_id: str | None = None


def decide_pose_input(
    pose_input: LocalPoseInput | None,
    *,
    previous_visible: bool,
) -> PersonSurfaceDecision:
    if pose_input is None:
        return PersonSurfaceDecision(
            visible=previous_visible,
            publish_pose=False,
            publish_last_seen=False,
        )

    normalized_frame = (pose_input.frame_id or "").strip()
    if normalized_frame != PERSON_POSE_FRAME:
        return PersonSurfaceDecision(
            visible=previous_visible,
            publish_pose=False,
            publish_last_seen=False,
        )

    return PersonSurfaceDecision(
        visible=True,
        publish_pose=True,
        publish_last_seen=True,
        pose_frame_id=PERSON_POSE_FRAME,
        last_seen_frame_id=PERSON_POSE_FRAME,
    )


def decide_visible_input(visible: bool) -> PersonSurfaceDecision:
    return PersonSurfaceDecision(
        visible=bool(visible),
        publish_pose=False,
        publish_last_seen=False,
    )
