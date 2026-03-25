// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from go2_apportation_msgs:srv/ReleaseObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__BUILDER_HPP_
#define GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "go2_apportation_msgs/srv/detail/release_object__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace go2_apportation_msgs
{

namespace srv
{

namespace builder
{

class Init_ReleaseObject_Request_verify_open
{
public:
  explicit Init_ReleaseObject_Request_verify_open(::go2_apportation_msgs::srv::ReleaseObject_Request & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::srv::ReleaseObject_Request verify_open(::go2_apportation_msgs::srv::ReleaseObject_Request::_verify_open_type arg)
  {
    msg_.verify_open = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::srv::ReleaseObject_Request msg_;
};

class Init_ReleaseObject_Request_release_mode
{
public:
  Init_ReleaseObject_Request_release_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ReleaseObject_Request_verify_open release_mode(::go2_apportation_msgs::srv::ReleaseObject_Request::_release_mode_type arg)
  {
    msg_.release_mode = std::move(arg);
    return Init_ReleaseObject_Request_verify_open(msg_);
  }

private:
  ::go2_apportation_msgs::srv::ReleaseObject_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::srv::ReleaseObject_Request>()
{
  return go2_apportation_msgs::srv::builder::Init_ReleaseObject_Request_release_mode();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace srv
{

namespace builder
{

class Init_ReleaseObject_Response_message
{
public:
  explicit Init_ReleaseObject_Response_message(::go2_apportation_msgs::srv::ReleaseObject_Response & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::srv::ReleaseObject_Response message(::go2_apportation_msgs::srv::ReleaseObject_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::srv::ReleaseObject_Response msg_;
};

class Init_ReleaseObject_Response_result_code
{
public:
  explicit Init_ReleaseObject_Response_result_code(::go2_apportation_msgs::srv::ReleaseObject_Response & msg)
  : msg_(msg)
  {}
  Init_ReleaseObject_Response_message result_code(::go2_apportation_msgs::srv::ReleaseObject_Response::_result_code_type arg)
  {
    msg_.result_code = std::move(arg);
    return Init_ReleaseObject_Response_message(msg_);
  }

private:
  ::go2_apportation_msgs::srv::ReleaseObject_Response msg_;
};

class Init_ReleaseObject_Response_success
{
public:
  Init_ReleaseObject_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ReleaseObject_Response_result_code success(::go2_apportation_msgs::srv::ReleaseObject_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_ReleaseObject_Response_result_code(msg_);
  }

private:
  ::go2_apportation_msgs::srv::ReleaseObject_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::srv::ReleaseObject_Response>()
{
  return go2_apportation_msgs::srv::builder::Init_ReleaseObject_Response_success();
}

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__BUILDER_HPP_
