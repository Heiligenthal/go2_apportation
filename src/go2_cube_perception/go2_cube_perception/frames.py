"""Frame constants for cube perception.

These names are consumed from the broader project TF contract. The owner
packages do not publish or redefine these frames.
"""

MAP = "map"
ODOM = "odom"
BASE_LINK = "base_link"
CAMERA_LINK = "camera_link"

FAST_OUTPUT_FRAME = ODOM
PRECISE_OUTPUT_FRAME = ODOM
LAST_SEEN_OUTPUT_FRAME = MAP
INTERNAL_TRACKING_FRAME = MAP
