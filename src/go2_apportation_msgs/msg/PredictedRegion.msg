# Public uncertainty region for predicted object location in /tracking/predicted_region.
# Public project-freeze semantics are map-based; motion-free shared surface.
std_msgs/Header header
geometry_msgs/Pose center
geometry_msgs/Vector3 size
float32 confidence
builtin_interfaces/Duration valid_for
