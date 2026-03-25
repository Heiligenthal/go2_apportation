// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from go2_apportation_msgs:msg/ObjectState.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__STRUCT_H_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance__struct.h"
// Member 'twist'
#include "geometry_msgs/msg/detail/twist_with_covariance__struct.h"

/// Struct defined in msg/ObjectState in the package go2_apportation_msgs.
/**
  * Phase-1 stub inferred from Document 002 text: pose + velocity + covariance for /tracking/object_state
 */
typedef struct go2_apportation_msgs__msg__ObjectState
{
  std_msgs__msg__Header header;
  geometry_msgs__msg__PoseWithCovariance pose;
  geometry_msgs__msg__TwistWithCovariance twist;
} go2_apportation_msgs__msg__ObjectState;

// Struct for a sequence of go2_apportation_msgs__msg__ObjectState.
typedef struct go2_apportation_msgs__msg__ObjectState__Sequence
{
  go2_apportation_msgs__msg__ObjectState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__msg__ObjectState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__STRUCT_H_
