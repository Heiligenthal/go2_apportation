from __future__ import annotations

from dataclasses import dataclass


RELEASE_MODE_OPEN_GRIPPER = 0
RELEASE_MODE_DROP_SAFE = 1
RELEASE_MODE_HANDOVER_RELEASE = 2

RELEASE_RESULT_SUCCESS = 0
RELEASE_RESULT_FAILED = 1
RELEASE_RESULT_TIMEOUT = 2
RELEASE_RESULT_SAFETY_ABORTED = 3


@dataclass(frozen=True)
class ReleaseMissionResult:
    release_mode: int
    result_code: int
    mission_result: str


def map_release_result_to_mission_result(release_mode: int, result_code: int) -> ReleaseMissionResult:
    normalized_mode = int(release_mode)
    normalized_result = int(result_code)

    if normalized_result == RELEASE_RESULT_TIMEOUT:
        mission_result = "RELEASE_TIMEOUT"
    elif normalized_result == RELEASE_RESULT_SAFETY_ABORTED:
        mission_result = "SAFETY_ABORTED"
    elif normalized_result == RELEASE_RESULT_SUCCESS:
        if normalized_mode == RELEASE_MODE_HANDOVER_RELEASE:
            mission_result = "HANDOVER_RELEASE_SUCCESS"
        elif normalized_mode == RELEASE_MODE_DROP_SAFE:
            mission_result = "DROP_RELEASE_SUCCESS"
        else:
            mission_result = "RELEASE_FAILED"
    else:
        mission_result = "RELEASE_FAILED"

    return ReleaseMissionResult(
        release_mode=normalized_mode,
        result_code=normalized_result,
        mission_result=mission_result,
    )
