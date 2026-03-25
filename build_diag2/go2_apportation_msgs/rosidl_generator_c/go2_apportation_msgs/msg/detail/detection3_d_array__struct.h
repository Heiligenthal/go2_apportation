// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from go2_apportation_msgs:msg/Detection3DArray.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D_ARRAY__STRUCT_H_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D_ARRAY__STRUCT_H_

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
// Member 'detections'
#include "go2_apportation_msgs/msg/detail/detection3_d__struct.h"

/// Struct defined in msg/Detection3DArray in the package go2_apportation_msgs.
/**
  * Document 002 baseline recommends a custom Detection3DArray message
 */
typedef struct go2_apportation_msgs__msg__Detection3DArray
{
  std_msgs__msg__Header header;
  go2_apportation_msgs__msg__Detection3D__Sequence detections;
} go2_apportation_msgs__msg__Detection3DArray;

// Struct for a sequence of go2_apportation_msgs__msg__Detection3DArray.
typedef struct go2_apportation_msgs__msg__Detection3DArray__Sequence
{
  go2_apportation_msgs__msg__Detection3DArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__msg__Detection3DArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D_ARRAY__STRUCT_H_
