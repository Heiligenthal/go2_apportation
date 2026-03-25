// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from go2_apportation_msgs:msg/ThrowStatus.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__STRUCT_H_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'IDLE'.
enum
{
  go2_apportation_msgs__msg__ThrowStatus__IDLE = 0
};

/// Constant 'HELD'.
enum
{
  go2_apportation_msgs__msg__ThrowStatus__HELD = 1
};

/// Constant 'RELEASE_SUSPECTED'.
enum
{
  go2_apportation_msgs__msg__ThrowStatus__RELEASE_SUSPECTED = 2
};

/// Constant 'THROWN'.
enum
{
  go2_apportation_msgs__msg__ThrowStatus__THROWN = 3
};

/// Constant 'LANDED'.
enum
{
  go2_apportation_msgs__msg__ThrowStatus__LANDED = 4
};

/// Constant 'LOST'.
enum
{
  go2_apportation_msgs__msg__ThrowStatus__LOST = 5
};

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/ThrowStatus in the package go2_apportation_msgs.
/**
  * Phase-1 stub for /tracking/throw_status enum values named in Document 002
 */
typedef struct go2_apportation_msgs__msg__ThrowStatus
{
  std_msgs__msg__Header header;
  uint8_t status;
} go2_apportation_msgs__msg__ThrowStatus;

// Struct for a sequence of go2_apportation_msgs__msg__ThrowStatus.
typedef struct go2_apportation_msgs__msg__ThrowStatus__Sequence
{
  go2_apportation_msgs__msg__ThrowStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__msg__ThrowStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__STRUCT_H_
