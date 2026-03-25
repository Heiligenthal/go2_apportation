// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from go2_apportation_msgs:msg/ObjectState.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__BUILDER_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "go2_apportation_msgs/msg/detail/object_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace go2_apportation_msgs
{

namespace msg
{

namespace builder
{

class Init_ObjectState_twist
{
public:
  explicit Init_ObjectState_twist(::go2_apportation_msgs::msg::ObjectState & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::msg::ObjectState twist(::go2_apportation_msgs::msg::ObjectState::_twist_type arg)
  {
    msg_.twist = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::msg::ObjectState msg_;
};

class Init_ObjectState_pose
{
public:
  explicit Init_ObjectState_pose(::go2_apportation_msgs::msg::ObjectState & msg)
  : msg_(msg)
  {}
  Init_ObjectState_twist pose(::go2_apportation_msgs::msg::ObjectState::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_ObjectState_twist(msg_);
  }

private:
  ::go2_apportation_msgs::msg::ObjectState msg_;
};

class Init_ObjectState_header
{
public:
  Init_ObjectState_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ObjectState_pose header(::go2_apportation_msgs::msg::ObjectState::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ObjectState_pose(msg_);
  }

private:
  ::go2_apportation_msgs::msg::ObjectState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::msg::ObjectState>()
{
  return go2_apportation_msgs::msg::builder::Init_ObjectState_header();
}

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__BUILDER_HPP_
