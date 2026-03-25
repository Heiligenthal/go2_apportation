// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from go2_apportation_msgs:msg/ThrowStatus.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__BUILDER_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "go2_apportation_msgs/msg/detail/throw_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace go2_apportation_msgs
{

namespace msg
{

namespace builder
{

class Init_ThrowStatus_status
{
public:
  explicit Init_ThrowStatus_status(::go2_apportation_msgs::msg::ThrowStatus & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::msg::ThrowStatus status(::go2_apportation_msgs::msg::ThrowStatus::_status_type arg)
  {
    msg_.status = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::msg::ThrowStatus msg_;
};

class Init_ThrowStatus_header
{
public:
  Init_ThrowStatus_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ThrowStatus_status header(::go2_apportation_msgs::msg::ThrowStatus::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ThrowStatus_status(msg_);
  }

private:
  ::go2_apportation_msgs::msg::ThrowStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::msg::ThrowStatus>()
{
  return go2_apportation_msgs::msg::builder::Init_ThrowStatus_header();
}

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__BUILDER_HPP_
