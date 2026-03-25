"""Backend type definitions for cube perception."""

from enum import Enum


class BackendKind(str, Enum):
    """Supported backend kinds for cube perception."""

    STUB = "stub"
    TENSORRT_STUB = "tensorrt_stub"
    BBOX_DEPTH_STUB = "bbox_depth_stub"
    SEGMENTATION_DEPTH_STUB = "segmentation_depth_stub"
