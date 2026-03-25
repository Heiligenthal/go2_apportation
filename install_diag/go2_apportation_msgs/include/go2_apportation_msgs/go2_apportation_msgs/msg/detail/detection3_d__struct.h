// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from go2_apportation_msgs:msg/Detection3D.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__STRUCT_H_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance__struct.h"

/// Struct defined in msg/Detection3D in the package go2_apportation_msgs.
/**
  * Document 002 baseline (tracking detection item)
 */
typedef struct go2_apportation_msgs__msg__Detection3D
{
  geometry_msgs__msg__PoseWithCovariance pose;
  float confidence;
  uint32_t class_id;
} go2_apportation_msgs__msg__Detection3D;

// Struct for a sequence of go2_apportation_msgs__msg__Detection3D.
typedef struct go2_apportation_msgs__msg__Detection3D__Sequence
{
  go2_apportation_msgs__msg__Detection3D * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__msg__Detection3D__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__STRUCT_H_
