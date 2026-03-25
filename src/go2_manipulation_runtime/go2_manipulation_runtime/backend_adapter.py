from __future__ import annotations

from dataclasses import dataclass

from .pick_result_mapping import (
    OBJECT_DROPPED,
    PICK_FAILED,
    PICK_SUCCESS,
    PICK_TIMEOUT,
    PICK_UNREACHABLE,
    SAFETY_ABORTED,
)
from .release_result_mapping import (
    RELEASE_RESULT_FAILED,
    RELEASE_RESULT_SAFETY_ABORTED,
    RELEASE_RESULT_SUCCESS,
    RELEASE_RESULT_TIMEOUT,
)


@dataclass(frozen=True)
class BackendPickOutcome:
    success: bool = False
    dropped: bool = False
    unreachable: bool = False
    timeout: bool = False
    safety_aborted: bool = False


@dataclass(frozen=True)
class BackendReleaseOutcome:
    success: bool = False
    timeout: bool = False
    safety_aborted: bool = False


def map_backend_pick_outcome_to_result_code(outcome: BackendPickOutcome) -> int:
    if outcome.safety_aborted:
        return SAFETY_ABORTED
    if outcome.timeout:
        return PICK_TIMEOUT
    if outcome.unreachable:
        return PICK_UNREACHABLE
    if outcome.dropped:
        return OBJECT_DROPPED
    if outcome.success:
        return PICK_SUCCESS
    return PICK_FAILED


def map_backend_release_outcome_to_result_code(outcome: BackendReleaseOutcome) -> int:
    if outcome.safety_aborted:
        return RELEASE_RESULT_SAFETY_ABORTED
    if outcome.timeout:
        return RELEASE_RESULT_TIMEOUT
    if outcome.success:
        return RELEASE_RESULT_SUCCESS
    return RELEASE_RESULT_FAILED
