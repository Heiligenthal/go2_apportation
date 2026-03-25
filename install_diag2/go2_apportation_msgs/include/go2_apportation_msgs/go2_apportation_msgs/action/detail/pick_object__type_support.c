// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from go2_apportation_msgs:action/PickObject.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
#include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "go2_apportation_msgs/action/detail/pick_object__functions.h"
#include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `target_pose`
#include "geometry_msgs/msg/pose_stamped.h"
// Member `target_pose`
#include "geometry_msgs/msg/detail/pose_stamped__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_Goal__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_Goal__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_member_array[6] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Goal, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "target_pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Goal, target_pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "object_class_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Goal, object_class_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "position_tolerance_m",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Goal, position_tolerance_m),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "orientation_tolerance_rad",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Goal, orientation_tolerance_rad),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "allow_replan",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Goal, allow_replan),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_Goal",  // message name
  6,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_Goal),
  go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_Goal)() {
  go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PoseStamped)();
  if (!go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_Goal__rosidl_typesupport_introspection_c__PickObject_Goal_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"
// Member `grasp_pose_used`
// already included above
// #include "geometry_msgs/msg/pose_stamped.h"
// Member `grasp_pose_used`
// already included above
// #include "geometry_msgs/msg/detail/pose_stamped__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_Result__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_Result__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_member_array[4] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Result, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "result_code",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Result, result_code),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Result, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "grasp_pose_used",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Result, grasp_pose_used),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_Result",  // message name
  4,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_Result),
  go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_Result)() {
  go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PoseStamped)();
  if (!go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_Result__rosidl_typesupport_introspection_c__PickObject_Result_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `stage_text`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_Feedback__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_Feedback__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_member_array[2] = {
  {
    "stage",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Feedback, stage),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "stage_text",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_Feedback, stage_text),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_Feedback",  // message name
  2,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_Feedback),
  go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_Feedback)() {
  if (!go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_Feedback__rosidl_typesupport_introspection_c__PickObject_Feedback_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `goal_id`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `goal`
#include "go2_apportation_msgs/action/pick_object.h"
// Member `goal`
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_SendGoal_Request__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_SendGoal_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_member_array[2] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_SendGoal_Request, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "goal",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_SendGoal_Request, goal),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_SendGoal_Request",  // message name
  2,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_SendGoal_Request),
  go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal_Request)() {
  go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_Goal)();
  if (!go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_SendGoal_Request__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_SendGoal_Response__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_SendGoal_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_member_array[2] = {
  {
    "accepted",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_SendGoal_Response, accepted),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_SendGoal_Response, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_SendGoal_Response",  // message name
  2,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_SendGoal_Response),
  go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal_Response)() {
  go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_SendGoal_Response__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_members = {
  "go2_apportation_msgs__action",  // service namespace
  "PickObject_SendGoal",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_Request_message_type_support_handle,
  NULL  // response message
  // go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_Response_message_type_support_handle
};

static rosidl_service_type_support_t go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_type_support_handle = {
  0,
  &go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal)() {
  if (!go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_SendGoal_Response)()->data;
  }

  return &go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_SendGoal_service_type_support_handle;
}

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_GetResult_Request__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_GetResult_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_member_array[1] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_GetResult_Request, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_GetResult_Request",  // message name
  1,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_GetResult_Request),
  go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult_Request)() {
  go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  if (!go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_GetResult_Request__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `result`
// already included above
// #include "go2_apportation_msgs/action/pick_object.h"
// Member `result`
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_GetResult_Response__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_GetResult_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_member_array[2] = {
  {
    "status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_GetResult_Response, status),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "result",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_GetResult_Response, result),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_GetResult_Response",  // message name
  2,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_GetResult_Response),
  go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult_Response)() {
  go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_Result)();
  if (!go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_GetResult_Response__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_members = {
  "go2_apportation_msgs__action",  // service namespace
  "PickObject_GetResult",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_Request_message_type_support_handle,
  NULL  // response message
  // go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_Response_message_type_support_handle
};

static rosidl_service_type_support_t go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_type_support_handle = {
  0,
  &go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult)() {
  if (!go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_GetResult_Response)()->data;
  }

  return &go2_apportation_msgs__action__detail__pick_object__rosidl_typesupport_introspection_c__PickObject_GetResult_service_type_support_handle;
}

// already included above
// #include <stddef.h>
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"
// already included above
// #include "go2_apportation_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__functions.h"
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `feedback`
// already included above
// #include "go2_apportation_msgs/action/pick_object.h"
// Member `feedback`
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  go2_apportation_msgs__action__PickObject_FeedbackMessage__init(message_memory);
}

void go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_fini_function(void * message_memory)
{
  go2_apportation_msgs__action__PickObject_FeedbackMessage__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_member_array[2] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_FeedbackMessage, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "feedback",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(go2_apportation_msgs__action__PickObject_FeedbackMessage, feedback),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_members = {
  "go2_apportation_msgs__action",  // message namespace
  "PickObject_FeedbackMessage",  // message name
  2,  // number of fields
  sizeof(go2_apportation_msgs__action__PickObject_FeedbackMessage),
  go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_member_array,  // message members
  go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_type_support_handle = {
  0,
  &go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_go2_apportation_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_FeedbackMessage)() {
  go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, go2_apportation_msgs, action, PickObject_Feedback)();
  if (!go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_type_support_handle.typesupport_identifier) {
    go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &go2_apportation_msgs__action__PickObject_FeedbackMessage__rosidl_typesupport_introspection_c__PickObject_FeedbackMessage_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
