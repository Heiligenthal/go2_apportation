// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from go2_apportation_msgs:msg/Detection3D.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__TRAITS_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "go2_apportation_msgs/msg/detail/detection3_d__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance__traits.hpp"

namespace go2_apportation_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Detection3D & msg,
  std::ostream & out)
{
  out << "{";
  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
    out << ", ";
  }

  // member: confidence
  {
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << ", ";
  }

  // member: class_id
  {
    out << "class_id: ";
    rosidl_generator_traits::value_to_yaml(msg.class_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Detection3D & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }

  // member: confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << "\n";
  }

  // member: class_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "class_id: ";
    rosidl_generator_traits::value_to_yaml(msg.class_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Detection3D & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::msg::Detection3D & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::msg::Detection3D & msg)
{
  return go2_apportation_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::msg::Detection3D>()
{
  return "go2_apportation_msgs::msg::Detection3D";
}

template<>
inline const char * name<go2_apportation_msgs::msg::Detection3D>()
{
  return "go2_apportation_msgs/msg/Detection3D";
}

template<>
struct has_fixed_size<go2_apportation_msgs::msg::Detection3D>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::PoseWithCovariance>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::msg::Detection3D>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::PoseWithCovariance>::value> {};

template<>
struct is_message<go2_apportation_msgs::msg::Detection3D>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__TRAITS_HPP_
