from __future__ import annotations

PERSON_VISIBLE_TOPIC = "/perception/person_visible"
PERSON_POSE_TOPIC = "/perception/person_pose"
PERSON_LAST_SEEN_TOPIC = "/perception/person_last_seen"
PERSON_POSE_FRAME = "map"

# Implementation-local adapter inputs only.
LOCAL_PERSON_POSE_INPUT_TOPIC = "~/input/person_pose_map"
LOCAL_PERSON_VISIBLE_INPUT_TOPIC = "~/input/person_visible"

# Stub-only note:
# Upstream person detections are intentionally not invented here. A later
# adapter may feed the node with real observations, but this package owns only
# the frozen output surface for now.
UPSTREAM_INPUTS_TODO: tuple[str, ...] = (
    "person detection source (not frozen in this package)",
    "TF availability for map-referenced outputs",
)
