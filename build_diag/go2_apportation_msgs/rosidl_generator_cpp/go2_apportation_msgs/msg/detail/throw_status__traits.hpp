// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from go2_apportation_msgs:msg/ThrowStatus.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__TRAITS_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "go2_apportation_msgs/msg/detail/throw_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace go2_apportation_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ThrowStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ThrowStatus & msg,
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

  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ThrowStatus & msg, bool use_flow_style = false)
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
  const go2_apportation_msgs::msg::ThrowStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::msg::ThrowStatus & msg)
{
  return go2_apportation_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::msg::ThrowStatus>()
{
  return "go2_apportation_msgs::msg::ThrowStatus";
}

template<>
inline const char * name<go2_apportation_msgs::msg::ThrowStatus>()
{
  return "go2_apportation_msgs/msg/ThrowStatus";
}

template<>
struct has_fixed_size<go2_apportation_msgs::msg::ThrowStatus>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<go2_apportation_msgs::msg::ThrowStatus>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<go2_apportation_msgs::msg::ThrowStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__TRAITS_HPP_
