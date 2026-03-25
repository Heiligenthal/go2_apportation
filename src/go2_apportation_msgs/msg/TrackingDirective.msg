# Compact tracking/perception recommendation channel for the orchestrator.
# Project-freeze contract: no geometry, no motion, no cmd_vel semantics.
std_msgs/Header header
uint8 NONE=0
uint8 REQUEST_INTERCEPT=1
uint8 REQUEST_LOCAL_SEARCH=2
uint8 REQUEST_GLOBAL_SEARCH=3
uint8 REQUEST_PICK_READY=4
uint8 REQUEST_PICK_ABORT=5

uint8 REASON_UNSPECIFIED=0
uint8 TARGET_NOT_CENTERABLE=1
uint8 TARGET_MOVING=2
uint8 TARGET_LOST=3
uint8 TARGET_STABLE=4
uint8 TARGET_NOT_VISIBLE=5
uint8 TARGET_MOVED_DURING_PICK=6

uint8 directive
uint8 reason
builtin_interfaces/Duration valid_for
