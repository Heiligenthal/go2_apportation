// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from go2_apportation_msgs:action/PickObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__STRUCT_H_
#define GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__STRUCT_H_

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
// Member 'target_pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_Goal
{
  std_msgs__msg__Header header;
  geometry_msgs__msg__PoseStamped target_pose;
  uint32_t object_class_id;
  float position_tolerance_m;
  float orientation_tolerance_rad;
  bool allow_replan;
} go2_apportation_msgs__action__PickObject_Goal;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_Goal.
typedef struct go2_apportation_msgs__action__PickObject_Goal__Sequence
{
  go2_apportation_msgs__action__PickObject_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"
// Member 'grasp_pose_used'
// already included above
// #include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_Result
{
  bool success;
  uint16_t result_code;
  rosidl_runtime_c__String message;
  geometry_msgs__msg__PoseStamped grasp_pose_used;
} go2_apportation_msgs__action__PickObject_Result;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_Result.
typedef struct go2_apportation_msgs__action__PickObject_Result__Sequence
{
  go2_apportation_msgs__action__PickObject_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stage_text'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_Feedback
{
  uint8_t stage;
  rosidl_runtime_c__String stage_text;
} go2_apportation_msgs__action__PickObject_Feedback;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_Feedback.
typedef struct go2_apportation_msgs__action__PickObject_Feedback__Sequence
{
  go2_apportation_msgs__action__PickObject_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "go2_apportation_msgs/action/detail/pick_object__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  go2_apportation_msgs__action__PickObject_Goal goal;
} go2_apportation_msgs__action__PickObject_SendGoal_Request;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_SendGoal_Request.
typedef struct go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence
{
  go2_apportation_msgs__action__PickObject_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} go2_apportation_msgs__action__PickObject_SendGoal_Response;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_SendGoal_Response.
typedef struct go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence
{
  go2_apportation_msgs__action__PickObject_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} go2_apportation_msgs__action__PickObject_GetResult_Request;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_GetResult_Request.
typedef struct go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence
{
  go2_apportation_msgs__action__PickObject_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_GetResult_Response
{
  int8_t status;
  go2_apportation_msgs__action__PickObject_Result result;
} go2_apportation_msgs__action__PickObject_GetResult_Response;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_GetResult_Response.
typedef struct go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence
{
  go2_apportation_msgs__action__PickObject_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"

/// Struct defined in action/PickObject in the package go2_apportation_msgs.
typedef struct go2_apportation_msgs__action__PickObject_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  go2_apportation_msgs__action__PickObject_Feedback feedback;
} go2_apportation_msgs__action__PickObject_FeedbackMessage;

// Struct for a sequence of go2_apportation_msgs__action__PickObject_FeedbackMessage.
typedef struct go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence
{
  go2_apportation_msgs__action__PickObject_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__STRUCT_H_
