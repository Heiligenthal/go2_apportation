from __future__ import annotations

from dataclasses import dataclass


PICK_SUCCESS = 0
PICK_FAILED = 1
OBJECT_DROPPED = 2
PICK_UNREACHABLE = 3
PICK_TIMEOUT = 4
SAFETY_ABORTED = 5

PICK_EVENT_BY_RESULT_CODE: dict[int, str] = {
    PICK_SUCCESS: "grasp_ok",
    PICK_FAILED: "grasp_failed",
    OBJECT_DROPPED: "object_dropped",
    PICK_UNREACHABLE: "object_unreachable",
    PICK_TIMEOUT: "timeout",
    SAFETY_ABORTED: "safety_abort",
}


@dataclass(frozen=True)
class PickEventMapping:
    result_code: int
    event_label: str


def map_pick_result_code_to_event(result_code: int) -> PickEventMapping:
    event_label = PICK_EVENT_BY_RESULT_CODE.get(int(result_code), "grasp_failed")
    return PickEventMapping(result_code=int(result_code), event_label=event_label)
