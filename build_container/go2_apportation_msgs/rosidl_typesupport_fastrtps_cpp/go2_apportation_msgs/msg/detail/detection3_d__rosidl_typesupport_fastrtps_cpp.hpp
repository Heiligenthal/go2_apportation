// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from go2_apportation_msgs:msg/Detection3D.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "go2_apportation_msgs/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "go2_apportation_msgs/msg/detail/detection3_d__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace go2_apportation_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_go2_apportation_msgs
cdr_serialize(
  const go2_apportation_msgs::msg::Detection3D & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_go2_apportation_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  go2_apportation_msgs::msg::Detection3D & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_go2_apportation_msgs
get_serialized_size(
  const go2_apportation_msgs::msg::Detection3D & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_go2_apportation_msgs
max_serialized_size_Detection3D(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace go2_apportation_msgs

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_go2_apportation_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, go2_apportation_msgs, msg, Detection3D)();

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
