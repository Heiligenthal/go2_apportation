# Public replannable intercept target for /tracking/intercept_goal.
# Public project-freeze semantics are map-based; motion-free shared surface.
std_msgs/Header header
geometry_msgs/PoseStamped target_pose
float32 approach_radius_m
float32 goal_tolerance_m
float32 confidence
builtin_interfaces/Duration valid_for
bool is_dynamic_estimate
