// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from go2_apportation_msgs:msg/Detection3D.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__STRUCT_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__go2_apportation_msgs__msg__Detection3D __attribute__((deprecated))
#else
# define DEPRECATED__go2_apportation_msgs__msg__Detection3D __declspec(deprecated)
#endif

namespace go2_apportation_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Detection3D_
{
  using Type = Detection3D_<ContainerAllocator>;

  explicit Detection3D_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->confidence = 0.0f;
      this->class_id = 0ul;
    }
  }

  explicit Detection3D_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->confidence = 0.0f;
      this->class_id = 0ul;
    }
  }

  // field types and members
  using _pose_type =
    geometry_msgs::msg::PoseWithCovariance_<ContainerAllocator>;
  _pose_type pose;
  using _confidence_type =
    float;
  _confidence_type confidence;
  using _class_id_type =
    uint32_t;
  _class_id_type class_id;

  // setters for named parameter idiom
  Type & set__pose(
    const geometry_msgs::msg::PoseWithCovariance_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }
  Type & set__confidence(
    const float & _arg)
  {
    this->confidence = _arg;
    return *this;
  }
  Type & set__class_id(
    const uint32_t & _arg)
  {
    this->class_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    go2_apportation_msgs::msg::Detection3D_<ContainerAllocator> *;
  using ConstRawPtr =
    const go2_apportation_msgs::msg::Detection3D_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::msg::Detection3D_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::msg::Detection3D_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__go2_apportation_msgs__msg__Detection3D
    std::shared_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__go2_apportation_msgs__msg__Detection3D
    std::shared_ptr<go2_apportation_msgs::msg::Detection3D_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Detection3D_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    if (this->confidence != other.confidence) {
      return false;
    }
    if (this->class_id != other.class_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const Detection3D_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Detection3D_

// alias to use template instance with default allocator
using Detection3D =
  go2_apportation_msgs::msg::Detection3D_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__DETECTION3_D__STRUCT_HPP_
