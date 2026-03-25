// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from go2_apportation_msgs:msg/ThrowStatus.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__STRUCT_HPP_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__STRUCT_HPP_

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

#ifndef _WIN32
# define DEPRECATED__go2_apportation_msgs__msg__ThrowStatus __attribute__((deprecated))
#else
# define DEPRECATED__go2_apportation_msgs__msg__ThrowStatus __declspec(deprecated)
#endif

namespace go2_apportation_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ThrowStatus_
{
  using Type = ThrowStatus_<ContainerAllocator>;

  explicit ThrowStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  explicit ThrowStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _status_type =
    uint8_t;
  _status_type status;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__status(
    const uint8_t & _arg)
  {
    this->status = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t IDLE =
    0u;
  static constexpr uint8_t HELD =
    1u;
  static constexpr uint8_t RELEASE_SUSPECTED =
    2u;
  static constexpr uint8_t THROWN =
    3u;
  static constexpr uint8_t LANDED =
    4u;
  static constexpr uint8_t LOST =
    5u;

  // pointer types
  using RawPtr =
    go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__go2_apportation_msgs__msg__ThrowStatus
    std::shared_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__go2_apportation_msgs__msg__ThrowStatus
    std::shared_ptr<go2_apportation_msgs::msg::ThrowStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ThrowStatus_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->status != other.status) {
      return false;
    }
    return true;
  }
  bool operator!=(const ThrowStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ThrowStatus_

// alias to use template instance with default allocator
using ThrowStatus =
  go2_apportation_msgs::msg::ThrowStatus_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ThrowStatus_<ContainerAllocator>::IDLE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ThrowStatus_<ContainerAllocator>::HELD;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ThrowStatus_<ContainerAllocator>::RELEASE_SUSPECTED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ThrowStatus_<ContainerAllocator>::THROWN;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ThrowStatus_<ContainerAllocator>::LANDED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ThrowStatus_<ContainerAllocator>::LOST;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__STRUCT_HPP_
