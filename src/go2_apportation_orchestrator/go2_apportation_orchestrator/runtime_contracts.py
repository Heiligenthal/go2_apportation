from __future__ import annotations

from .transition_spec import TransitionState

# Technical runtime contracts mirrored from Document 002 where available.
# Additional entries in this file are explicit project-freeze decisions and not
# retroactively treated as if they came from Document 002.

FRAME_BASE_LINK_NAV2 = "base_link_nav2"
LEGACY_DEBUG_FRAME_ODOM_NAV2 = "odom_nav2"

TOPIC_CMD_VEL_NAV2 = "/cmd_vel_nav2"
TOPIC_LOOK_YAW_DELTA = "/look_yaw_delta"
TOPIC_BALANCE_RPY_CMD = "/balance_rpy_cmd"
TOPIC_CONTROL_MODE_CMD = "/control_mode_cmd"
TOPIC_TRACKING_INTERCEPT_GOAL = "/tracking/intercept_goal"
TOPIC_TRACKING_PREDICTED_REGION = "/tracking/predicted_region"
TOPIC_TRACKING_DIRECTIVE = "/tracking/tracking_directive"

CONTROL_MODE_VELOCITY_MOVE = "velocity_move"
CONTROL_MODE_BALANCE_STAND = "balance_stand"

TRACKING_DIRECTIVE_EVENT_NAMES: dict[str, str] = {
    "REQUEST_INTERCEPT": "request_intercept",
    "REQUEST_LOCAL_SEARCH": "request_local_search",
    "REQUEST_GLOBAL_SEARCH": "request_global_search",
    "REQUEST_PICK_READY": "request_pick_ready",
    "REQUEST_PICK_ABORT": "request_pick_abort",
}

STATE_CONTROL_MODE_BASELINE: dict[TransitionState, str] = {
    TransitionState.INTERCEPT: CONTROL_MODE_VELOCITY_MOVE,
    TransitionState.SEARCH_OBJECT_LOCAL: CONTROL_MODE_VELOCITY_MOVE,
    TransitionState.OBSERVE_HAND: CONTROL_MODE_BALANCE_STAND,
}

# Explicit project-freeze note:
# - SEARCH_OBJECT_LOCAL stays in velocity_move.
# - Look regulation is direct Perception/Tracking -> Bridge and not routed
#   through the orchestrator.
# - PICK_REACQUIRE is not part of the current runtime state set and is
#   therefore documented only in freeze artifacts, not added as a state here.
