// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from go2_apportation_msgs:msg/ObjectState.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__STRUCT_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance__struct.hpp"
// Member 'twist'
#include "geometry_msgs/msg/detail/twist_with_covariance__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__go2_apportation_msgs__msg__ObjectState __attribute__((deprecated))
#else
# define DEPRECATED__go2_apportation_msgs__msg__ObjectState __declspec(deprecated)
#endif

namespace go2_apportation_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ObjectState_
{
  using Type = ObjectState_<ContainerAllocator>;

  explicit ObjectState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    pose(_init),
    twist(_init)
  {
    (void)_init;
  }

  explicit ObjectState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    pose(_alloc, _init),
    twist(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _pose_type =
    geometry_msgs::msg::PoseWithCovariance_<ContainerAllocator>;
  _pose_type pose;
  using _twist_type =
    geometry_msgs::msg::TwistWithCovariance_<ContainerAllocator>;
  _twist_type twist;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__pose(
    const geometry_msgs::msg::PoseWithCovariance_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }
  Type & set__twist(
    const geometry_msgs::msg::TwistWithCovariance_<ContainerAllocator> & _arg)
  {
    this->twist = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    go2_apportation_msgs::msg::ObjectState_<ContainerAllocator> *;
  using ConstRawPtr =
    const go2_apportation_msgs::msg::ObjectState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::msg::ObjectState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::msg::ObjectState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__go2_apportation_msgs__msg__ObjectState
    std::shared_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__go2_apportation_msgs__msg__ObjectState
    std::shared_ptr<go2_apportation_msgs::msg::ObjectState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ObjectState_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    if (this->twist != other.twist) {
      return false;
    }
    return true;
  }
  bool operator!=(const ObjectState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ObjectState_

// alias to use template instance with default allocator
using ObjectState =
  go2_apportation_msgs::msg::ObjectState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__OBJECT_STATE__STRUCT_HPP_
