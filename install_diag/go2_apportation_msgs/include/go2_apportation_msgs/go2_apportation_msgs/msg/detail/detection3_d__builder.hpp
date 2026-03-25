// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from go2_apportation_msgs:msg/Detection3D.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__BUILDER_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "go2_apportation_msgs/msg/detail/detection3_d__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace go2_apportation_msgs
{

namespace msg
{

namespace builder
{

class Init_Detection3D_class_id
{
public:
  explicit Init_Detection3D_class_id(::go2_apportation_msgs::msg::Detection3D & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::msg::Detection3D class_id(::go2_apportation_msgs::msg::Detection3D::_class_id_type arg)
  {
    msg_.class_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::msg::Detection3D msg_;
};

class Init_Detection3D_confidence
{
public:
  explicit Init_Detection3D_confidence(::go2_apportation_msgs::msg::Detection3D & msg)
  : msg_(msg)
  {}
  Init_Detection3D_class_id confidence(::go2_apportation_msgs::msg::Detection3D::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return Init_Detection3D_class_id(msg_);
  }

private:
  ::go2_apportation_msgs::msg::Detection3D msg_;
};

class Init_Detection3D_pose
{
public:
  Init_Detection3D_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Detection3D_confidence pose(::go2_apportation_msgs::msg::Detection3D::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_Detection3D_confidence(msg_);
  }

private:
  ::go2_apportation_msgs::msg::Detection3D msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::msg::Detection3D>()
{
  return go2_apportation_msgs::msg::builder::Init_Detection3D_pose();
}

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__BUILDER_HPP_
