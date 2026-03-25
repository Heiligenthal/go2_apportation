// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from go2_apportation_msgs:action/PickObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__TRAITS_HPP_
#define GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "go2_apportation_msgs/action/detail/pick_object__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'target_pose'
#include "geometry_msgs/msg/detail/pose_stamped__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_Goal & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: target_pose
  {
    out << "target_pose: ";
    to_flow_style_yaml(msg.target_pose, out);
    out << ", ";
  }

  // member: object_class_id
  {
    out << "object_class_id: ";
    rosidl_generator_traits::value_to_yaml(msg.object_class_id, out);
    out << ", ";
  }

  // member: position_tolerance_m
  {
    out << "position_tolerance_m: ";
    rosidl_generator_traits::value_to_yaml(msg.position_tolerance_m, out);
    out << ", ";
  }

  // member: orientation_tolerance_rad
  {
    out << "orientation_tolerance_rad: ";
    rosidl_generator_traits::value_to_yaml(msg.orientation_tolerance_rad, out);
    out << ", ";
  }

  // member: allow_replan
  {
    out << "allow_replan: ";
    rosidl_generator_traits::value_to_yaml(msg.allow_replan, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: target_pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "target_pose:\n";
    to_block_style_yaml(msg.target_pose, out, indentation + 2);
  }

  // member: object_class_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "object_class_id: ";
    rosidl_generator_traits::value_to_yaml(msg.object_class_id, out);
    out << "\n";
  }

  // member: position_tolerance_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "position_tolerance_m: ";
    rosidl_generator_traits::value_to_yaml(msg.position_tolerance_m, out);
    out << "\n";
  }

  // member: orientation_tolerance_rad
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "orientation_tolerance_rad: ";
    rosidl_generator_traits::value_to_yaml(msg.orientation_tolerance_rad, out);
    out << "\n";
  }

  // member: allow_replan
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "allow_replan: ";
    rosidl_generator_traits::value_to_yaml(msg.allow_replan, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_Goal & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_Goal & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_Goal>()
{
  return "go2_apportation_msgs::action::PickObject_Goal";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_Goal>()
{
  return "go2_apportation_msgs/action/PickObject_Goal";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_Goal>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::PoseStamped>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_Goal>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::PoseStamped>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_Goal>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'grasp_pose_used'
// already included above
// #include "geometry_msgs/msg/detail/pose_stamped__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_Result & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: result_code
  {
    out << "result_code: ";
    rosidl_generator_traits::value_to_yaml(msg.result_code, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << ", ";
  }

  // member: grasp_pose_used
  {
    out << "grasp_pose_used: ";
    to_flow_style_yaml(msg.grasp_pose_used, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_Result & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: result_code
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "result_code: ";
    rosidl_generator_traits::value_to_yaml(msg.result_code, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }

  // member: grasp_pose_used
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "grasp_pose_used:\n";
    to_block_style_yaml(msg.grasp_pose_used, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_Result & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_Result & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_Result & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_Result>()
{
  return "go2_apportation_msgs::action::PickObject_Result";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_Result>()
{
  return "go2_apportation_msgs/action/PickObject_Result";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_Result>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_Result>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_Result>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_Feedback & msg,
  std::ostream & out)
{
  out << "{";
  // member: stage
  {
    out << "stage: ";
    rosidl_generator_traits::value_to_yaml(msg.stage, out);
    out << ", ";
  }

  // member: stage_text
  {
    out << "stage_text: ";
    rosidl_generator_traits::value_to_yaml(msg.stage_text, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: stage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stage: ";
    rosidl_generator_traits::value_to_yaml(msg.stage, out);
    out << "\n";
  }

  // member: stage_text
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stage_text: ";
    rosidl_generator_traits::value_to_yaml(msg.stage_text, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_Feedback & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_Feedback & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_Feedback>()
{
  return "go2_apportation_msgs::action::PickObject_Feedback";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_Feedback>()
{
  return "go2_apportation_msgs/action/PickObject_Feedback";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_Feedback>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'goal'
#include "go2_apportation_msgs/action/detail/pick_object__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_SendGoal_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: goal
  {
    out << "goal: ";
    to_flow_style_yaml(msg.goal, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: goal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal:\n";
    to_block_style_yaml(msg.goal, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_SendGoal_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_SendGoal_Request & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_SendGoal_Request>()
{
  return "go2_apportation_msgs::action::PickObject_SendGoal_Request";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_SendGoal_Request>()
{
  return "go2_apportation_msgs/action/PickObject_SendGoal_Request";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_SendGoal_Request>
  : std::integral_constant<bool, has_fixed_size<go2_apportation_msgs::action::PickObject_Goal>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_SendGoal_Request>
  : std::integral_constant<bool, has_bounded_size<go2_apportation_msgs::action::PickObject_Goal>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_SendGoal_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_SendGoal_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: accepted
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << "\n";
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_SendGoal_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_SendGoal_Response & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_SendGoal_Response>()
{
  return "go2_apportation_msgs::action::PickObject_SendGoal_Response";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_SendGoal_Response>()
{
  return "go2_apportation_msgs/action/PickObject_SendGoal_Response";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_SendGoal_Response>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_SendGoal_Response>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_SendGoal_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_SendGoal>()
{
  return "go2_apportation_msgs::action::PickObject_SendGoal";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_SendGoal>()
{
  return "go2_apportation_msgs/action/PickObject_SendGoal";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_SendGoal>
  : std::integral_constant<
    bool,
    has_fixed_size<go2_apportation_msgs::action::PickObject_SendGoal_Request>::value &&
    has_fixed_size<go2_apportation_msgs::action::PickObject_SendGoal_Response>::value
  >
{
};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_SendGoal>
  : std::integral_constant<
    bool,
    has_bounded_size<go2_apportation_msgs::action::PickObject_SendGoal_Request>::value &&
    has_bounded_size<go2_apportation_msgs::action::PickObject_SendGoal_Response>::value
  >
{
};

template<>
struct is_service<go2_apportation_msgs::action::PickObject_SendGoal>
  : std::true_type
{
};

template<>
struct is_service_request<go2_apportation_msgs::action::PickObject_SendGoal_Request>
  : std::true_type
{
};

template<>
struct is_service_response<go2_apportation_msgs::action::PickObject_SendGoal_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_GetResult_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_GetResult_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_GetResult_Request & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_GetResult_Request>()
{
  return "go2_apportation_msgs::action::PickObject_GetResult_Request";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_GetResult_Request>()
{
  return "go2_apportation_msgs/action/PickObject_GetResult_Request";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_GetResult_Request>
  : std::integral_constant<bool, has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_GetResult_Request>
  : std::integral_constant<bool, has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_GetResult_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'result'
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_GetResult_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << ", ";
  }

  // member: result
  {
    out << "result: ";
    to_flow_style_yaml(msg.result, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }

  // member: result
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "result:\n";
    to_block_style_yaml(msg.result, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_GetResult_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_GetResult_Response & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_GetResult_Response>()
{
  return "go2_apportation_msgs::action::PickObject_GetResult_Response";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_GetResult_Response>()
{
  return "go2_apportation_msgs/action/PickObject_GetResult_Response";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_GetResult_Response>
  : std::integral_constant<bool, has_fixed_size<go2_apportation_msgs::action::PickObject_Result>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_GetResult_Response>
  : std::integral_constant<bool, has_bounded_size<go2_apportation_msgs::action::PickObject_Result>::value> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_GetResult_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_GetResult>()
{
  return "go2_apportation_msgs::action::PickObject_GetResult";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_GetResult>()
{
  return "go2_apportation_msgs/action/PickObject_GetResult";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_GetResult>
  : std::integral_constant<
    bool,
    has_fixed_size<go2_apportation_msgs::action::PickObject_GetResult_Request>::value &&
    has_fixed_size<go2_apportation_msgs::action::PickObject_GetResult_Response>::value
  >
{
};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_GetResult>
  : std::integral_constant<
    bool,
    has_bounded_size<go2_apportation_msgs::action::PickObject_GetResult_Request>::value &&
    has_bounded_size<go2_apportation_msgs::action::PickObject_GetResult_Response>::value
  >
{
};

template<>
struct is_service<go2_apportation_msgs::action::PickObject_GetResult>
  : std::true_type
{
};

template<>
struct is_service_request<go2_apportation_msgs::action::PickObject_GetResult_Request>
  : std::true_type
{
};

template<>
struct is_service_response<go2_apportation_msgs::action::PickObject_GetResult_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'feedback'
// already included above
// #include "go2_apportation_msgs/action/detail/pick_object__traits.hpp"

namespace go2_apportation_msgs
{

namespace action
{

inline void to_flow_style_yaml(
  const PickObject_FeedbackMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: feedback
  {
    out << "feedback: ";
    to_flow_style_yaml(msg.feedback, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickObject_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: feedback
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedback:\n";
    to_block_style_yaml(msg.feedback, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickObject_FeedbackMessage & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::action::PickObject_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::action::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::action::PickObject_FeedbackMessage & msg)
{
  return go2_apportation_msgs::action::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::action::PickObject_FeedbackMessage>()
{
  return "go2_apportation_msgs::action::PickObject_FeedbackMessage";
}

template<>
inline const char * name<go2_apportation_msgs::action::PickObject_FeedbackMessage>()
{
  return "go2_apportation_msgs/action/PickObject_FeedbackMessage";
}

template<>
struct has_fixed_size<go2_apportation_msgs::action::PickObject_FeedbackMessage>
  : std::integral_constant<bool, has_fixed_size<go2_apportation_msgs::action::PickObject_Feedback>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::action::PickObject_FeedbackMessage>
  : std::integral_constant<bool, has_bounded_size<go2_apportation_msgs::action::PickObject_Feedback>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<go2_apportation_msgs::action::PickObject_FeedbackMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits


namespace rosidl_generator_traits
{

template<>
struct is_action<go2_apportation_msgs::action::PickObject>
  : std::true_type
{
};

template<>
struct is_action_goal<go2_apportation_msgs::action::PickObject_Goal>
  : std::true_type
{
};

template<>
struct is_action_result<go2_apportation_msgs::action::PickObject_Result>
  : std::true_type
{
};

template<>
struct is_action_feedback<go2_apportation_msgs::action::PickObject_Feedback>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits


#endif  // GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__TRAITS_HPP_
