// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from go2_apportation_msgs:action/PickObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__BUILDER_HPP_
#define GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "go2_apportation_msgs/action/detail/pick_object__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_Goal_allow_replan
{
public:
  explicit Init_PickObject_Goal_allow_replan(::go2_apportation_msgs::action::PickObject_Goal & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_Goal allow_replan(::go2_apportation_msgs::action::PickObject_Goal::_allow_replan_type arg)
  {
    msg_.allow_replan = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Goal msg_;
};

class Init_PickObject_Goal_orientation_tolerance_rad
{
public:
  explicit Init_PickObject_Goal_orientation_tolerance_rad(::go2_apportation_msgs::action::PickObject_Goal & msg)
  : msg_(msg)
  {}
  Init_PickObject_Goal_allow_replan orientation_tolerance_rad(::go2_apportation_msgs::action::PickObject_Goal::_orientation_tolerance_rad_type arg)
  {
    msg_.orientation_tolerance_rad = std::move(arg);
    return Init_PickObject_Goal_allow_replan(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Goal msg_;
};

class Init_PickObject_Goal_position_tolerance_m
{
public:
  explicit Init_PickObject_Goal_position_tolerance_m(::go2_apportation_msgs::action::PickObject_Goal & msg)
  : msg_(msg)
  {}
  Init_PickObject_Goal_orientation_tolerance_rad position_tolerance_m(::go2_apportation_msgs::action::PickObject_Goal::_position_tolerance_m_type arg)
  {
    msg_.position_tolerance_m = std::move(arg);
    return Init_PickObject_Goal_orientation_tolerance_rad(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Goal msg_;
};

class Init_PickObject_Goal_object_class_id
{
public:
  explicit Init_PickObject_Goal_object_class_id(::go2_apportation_msgs::action::PickObject_Goal & msg)
  : msg_(msg)
  {}
  Init_PickObject_Goal_position_tolerance_m object_class_id(::go2_apportation_msgs::action::PickObject_Goal::_object_class_id_type arg)
  {
    msg_.object_class_id = std::move(arg);
    return Init_PickObject_Goal_position_tolerance_m(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Goal msg_;
};

class Init_PickObject_Goal_target_pose
{
public:
  explicit Init_PickObject_Goal_target_pose(::go2_apportation_msgs::action::PickObject_Goal & msg)
  : msg_(msg)
  {}
  Init_PickObject_Goal_object_class_id target_pose(::go2_apportation_msgs::action::PickObject_Goal::_target_pose_type arg)
  {
    msg_.target_pose = std::move(arg);
    return Init_PickObject_Goal_object_class_id(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Goal msg_;
};

class Init_PickObject_Goal_header
{
public:
  Init_PickObject_Goal_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_Goal_target_pose header(::go2_apportation_msgs::action::PickObject_Goal::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_PickObject_Goal_target_pose(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_Goal>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_Goal_header();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_Result_grasp_pose_used
{
public:
  explicit Init_PickObject_Result_grasp_pose_used(::go2_apportation_msgs::action::PickObject_Result & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_Result grasp_pose_used(::go2_apportation_msgs::action::PickObject_Result::_grasp_pose_used_type arg)
  {
    msg_.grasp_pose_used = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Result msg_;
};

class Init_PickObject_Result_message
{
public:
  explicit Init_PickObject_Result_message(::go2_apportation_msgs::action::PickObject_Result & msg)
  : msg_(msg)
  {}
  Init_PickObject_Result_grasp_pose_used message(::go2_apportation_msgs::action::PickObject_Result::_message_type arg)
  {
    msg_.message = std::move(arg);
    return Init_PickObject_Result_grasp_pose_used(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Result msg_;
};

class Init_PickObject_Result_result_code
{
public:
  explicit Init_PickObject_Result_result_code(::go2_apportation_msgs::action::PickObject_Result & msg)
  : msg_(msg)
  {}
  Init_PickObject_Result_message result_code(::go2_apportation_msgs::action::PickObject_Result::_result_code_type arg)
  {
    msg_.result_code = std::move(arg);
    return Init_PickObject_Result_message(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Result msg_;
};

class Init_PickObject_Result_success
{
public:
  Init_PickObject_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_Result_result_code success(::go2_apportation_msgs::action::PickObject_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_PickObject_Result_result_code(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_Result>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_Result_success();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_Feedback_stage_text
{
public:
  explicit Init_PickObject_Feedback_stage_text(::go2_apportation_msgs::action::PickObject_Feedback & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_Feedback stage_text(::go2_apportation_msgs::action::PickObject_Feedback::_stage_text_type arg)
  {
    msg_.stage_text = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Feedback msg_;
};

class Init_PickObject_Feedback_stage
{
public:
  Init_PickObject_Feedback_stage()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_Feedback_stage_text stage(::go2_apportation_msgs::action::PickObject_Feedback::_stage_type arg)
  {
    msg_.stage = std::move(arg);
    return Init_PickObject_Feedback_stage_text(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_Feedback>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_Feedback_stage();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_SendGoal_Request_goal
{
public:
  explicit Init_PickObject_SendGoal_Request_goal(::go2_apportation_msgs::action::PickObject_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_SendGoal_Request goal(::go2_apportation_msgs::action::PickObject_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_SendGoal_Request msg_;
};

class Init_PickObject_SendGoal_Request_goal_id
{
public:
  Init_PickObject_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_SendGoal_Request_goal goal_id(::go2_apportation_msgs::action::PickObject_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_PickObject_SendGoal_Request_goal(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_SendGoal_Request>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_SendGoal_Request_goal_id();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_SendGoal_Response_stamp
{
public:
  explicit Init_PickObject_SendGoal_Response_stamp(::go2_apportation_msgs::action::PickObject_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_SendGoal_Response stamp(::go2_apportation_msgs::action::PickObject_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_SendGoal_Response msg_;
};

class Init_PickObject_SendGoal_Response_accepted
{
public:
  Init_PickObject_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_SendGoal_Response_stamp accepted(::go2_apportation_msgs::action::PickObject_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_PickObject_SendGoal_Response_stamp(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_SendGoal_Response>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_SendGoal_Response_accepted();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_GetResult_Request_goal_id
{
public:
  Init_PickObject_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::go2_apportation_msgs::action::PickObject_GetResult_Request goal_id(::go2_apportation_msgs::action::PickObject_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_GetResult_Request>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_GetResult_Request_goal_id();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_GetResult_Response_result
{
public:
  explicit Init_PickObject_GetResult_Response_result(::go2_apportation_msgs::action::PickObject_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_GetResult_Response result(::go2_apportation_msgs::action::PickObject_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_GetResult_Response msg_;
};

class Init_PickObject_GetResult_Response_status
{
public:
  Init_PickObject_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_GetResult_Response_result status(::go2_apportation_msgs::action::PickObject_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_PickObject_GetResult_Response_result(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_GetResult_Response>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_GetResult_Response_status();
}

}  // namespace go2_apportation_msgs


namespace go2_apportation_msgs
{

namespace action
{

namespace builder
{

class Init_PickObject_FeedbackMessage_feedback
{
public:
  explicit Init_PickObject_FeedbackMessage_feedback(::go2_apportation_msgs::action::PickObject_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::go2_apportation_msgs::action::PickObject_FeedbackMessage feedback(::go2_apportation_msgs::action::PickObject_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_FeedbackMessage msg_;
};

class Init_PickObject_FeedbackMessage_goal_id
{
public:
  Init_PickObject_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickObject_FeedbackMessage_feedback goal_id(::go2_apportation_msgs::action::PickObject_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_PickObject_FeedbackMessage_feedback(msg_);
  }

private:
  ::go2_apportation_msgs::action::PickObject_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::go2_apportation_msgs::action::PickObject_FeedbackMessage>()
{
  return go2_apportation_msgs::action::builder::Init_PickObject_FeedbackMessage_goal_id();
}

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__BUILDER_HPP_
