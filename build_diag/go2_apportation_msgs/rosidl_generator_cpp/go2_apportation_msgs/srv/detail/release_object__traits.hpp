// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from go2_apportation_msgs:srv/ReleaseObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__TRAITS_HPP_
#define GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "go2_apportation_msgs/srv/detail/release_object__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace go2_apportation_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const ReleaseObject_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: release_mode
  {
    out << "release_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.release_mode, out);
    out << ", ";
  }

  // member: verify_open
  {
    out << "verify_open: ";
    rosidl_generator_traits::value_to_yaml(msg.verify_open, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ReleaseObject_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: release_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "release_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.release_mode, out);
    out << "\n";
  }

  // member: verify_open
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "verify_open: ";
    rosidl_generator_traits::value_to_yaml(msg.verify_open, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ReleaseObject_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::srv::ReleaseObject_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::srv::ReleaseObject_Request & msg)
{
  return go2_apportation_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::srv::ReleaseObject_Request>()
{
  return "go2_apportation_msgs::srv::ReleaseObject_Request";
}

template<>
inline const char * name<go2_apportation_msgs::srv::ReleaseObject_Request>()
{
  return "go2_apportation_msgs/srv/ReleaseObject_Request";
}

template<>
struct has_fixed_size<go2_apportation_msgs::srv::ReleaseObject_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<go2_apportation_msgs::srv::ReleaseObject_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<go2_apportation_msgs::srv::ReleaseObject_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace go2_apportation_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const ReleaseObject_Response & msg,
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
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ReleaseObject_Response & msg,
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
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ReleaseObject_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace go2_apportation_msgs

namespace rosidl_generator_traits
{

[[deprecated("use go2_apportation_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const go2_apportation_msgs::srv::ReleaseObject_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  go2_apportation_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use go2_apportation_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const go2_apportation_msgs::srv::ReleaseObject_Response & msg)
{
  return go2_apportation_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<go2_apportation_msgs::srv::ReleaseObject_Response>()
{
  return "go2_apportation_msgs::srv::ReleaseObject_Response";
}

template<>
inline const char * name<go2_apportation_msgs::srv::ReleaseObject_Response>()
{
  return "go2_apportation_msgs/srv/ReleaseObject_Response";
}

template<>
struct has_fixed_size<go2_apportation_msgs::srv::ReleaseObject_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<go2_apportation_msgs::srv::ReleaseObject_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<go2_apportation_msgs::srv::ReleaseObject_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<go2_apportation_msgs::srv::ReleaseObject>()
{
  return "go2_apportation_msgs::srv::ReleaseObject";
}

template<>
inline const char * name<go2_apportation_msgs::srv::ReleaseObject>()
{
  return "go2_apportation_msgs/srv/ReleaseObject";
}

template<>
struct has_fixed_size<go2_apportation_msgs::srv::ReleaseObject>
  : std::integral_constant<
    bool,
    has_fixed_size<go2_apportation_msgs::srv::ReleaseObject_Request>::value &&
    has_fixed_size<go2_apportation_msgs::srv::ReleaseObject_Response>::value
  >
{
};

template<>
struct has_bounded_size<go2_apportation_msgs::srv::ReleaseObject>
  : std::integral_constant<
    bool,
    has_bounded_size<go2_apportation_msgs::srv::ReleaseObject_Request>::value &&
    has_bounded_size<go2_apportation_msgs::srv::ReleaseObject_Response>::value
  >
{
};

template<>
struct is_service<go2_apportation_msgs::srv::ReleaseObject>
  : std::true_type
{
};

template<>
struct is_service_request<go2_apportation_msgs::srv::ReleaseObject_Request>
  : std::true_type
{
};

template<>
struct is_service_response<go2_apportation_msgs::srv::ReleaseObject_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__TRAITS_HPP_
