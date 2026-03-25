// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from go2_apportation_msgs:srv/ReleaseObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__STRUCT_H_
#define GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'OPEN_GRIPPER'.
enum
{
  go2_apportation_msgs__srv__ReleaseObject_Request__OPEN_GRIPPER = 0
};

/// Constant 'DROP_SAFE'.
enum
{
  go2_apportation_msgs__srv__ReleaseObject_Request__DROP_SAFE = 1
};

/// Constant 'HANDOVER_RELEASE'.
enum
{
  go2_apportation_msgs__srv__ReleaseObject_Request__HANDOVER_RELEASE = 2
};

/// Struct defined in srv/ReleaseObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__srv__ReleaseObject_Request
{
  uint8_t release_mode;
  bool verify_open;
} go2_apportation_msgs__srv__ReleaseObject_Request;

// Struct for a sequence of go2_apportation_msgs__srv__ReleaseObject_Request.
typedef struct go2_apportation_msgs__srv__ReleaseObject_Request__Sequence
{
  go2_apportation_msgs__srv__ReleaseObject_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__srv__ReleaseObject_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ReleaseObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__srv__ReleaseObject_Response
{
  bool success;
  uint16_t result_code;
  rosidl_runtime_c__String message;
} go2_apportation_msgs__srv__ReleaseObject_Response;

// Struct for a sequence of go2_apportation_msgs__srv__ReleaseObject_Response.
typedef struct go2_apportation_msgs__srv__ReleaseObject_Response__Sequence
{
  go2_apportation_msgs__srv__ReleaseObject_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__srv__ReleaseObject_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__STRUCT_H_
