// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from go2_apportation_msgs:srv/ReleaseObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__STRUCT_HPP_
#define GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Request __attribute__((deprecated))
#else
# define DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Request __declspec(deprecated)
#endif

namespace go2_apportation_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ReleaseObject_Request_
{
  using Type = ReleaseObject_Request_<ContainerAllocator>;

  explicit ReleaseObject_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->release_mode = 0;
      this->verify_open = false;
    }
  }

  explicit ReleaseObject_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->release_mode = 0;
      this->verify_open = false;
    }
  }

  // field types and members
  using _release_mode_type =
    uint8_t;
  _release_mode_type release_mode;
  using _verify_open_type =
    bool;
  _verify_open_type verify_open;

  // setters for named parameter idiom
  Type & set__release_mode(
    const uint8_t & _arg)
  {
    this->release_mode = _arg;
    return *this;
  }
  Type & set__verify_open(
    const bool & _arg)
  {
    this->verify_open = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t OPEN_GRIPPER =
    0u;
  static constexpr uint8_t DROP_SAFE =
    1u;
  static constexpr uint8_t HANDOVER_RELEASE =
    2u;

  // pointer types
  using RawPtr =
    go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Request
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Request
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ReleaseObject_Request_ & other) const
  {
    if (this->release_mode != other.release_mode) {
      return false;
    }
    if (this->verify_open != other.verify_open) {
      return false;
    }
    return true;
  }
  bool operator!=(const ReleaseObject_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ReleaseObject_Request_

// alias to use template instance with default allocator
using ReleaseObject_Request =
  go2_apportation_msgs::srv::ReleaseObject_Request_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ReleaseObject_Request_<ContainerAllocator>::OPEN_GRIPPER;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ReleaseObject_Request_<ContainerAllocator>::DROP_SAFE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ReleaseObject_Request_<ContainerAllocator>::HANDOVER_RELEASE;
#endif  // __cplusplus < 201703L

}  // namespace srv

}  // namespace go2_apportation_msgs


#ifndef _WIN32
# define DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Response __attribute__((deprecated))
#else
# define DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Response __declspec(deprecated)
#endif

namespace go2_apportation_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ReleaseObject_Response_
{
  using Type = ReleaseObject_Response_<ContainerAllocator>;

  explicit ReleaseObject_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->result_code = 0;
      this->message = "";
    }
  }

  explicit ReleaseObject_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->result_code = 0;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _result_code_type =
    uint16_t;
  _result_code_type result_code;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__result_code(
    const uint16_t & _arg)
  {
    this->result_code = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Response
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__go2_apportation_msgs__srv__ReleaseObject_Response
    std::shared_ptr<go2_apportation_msgs::srv::ReleaseObject_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ReleaseObject_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->result_code != other.result_code) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const ReleaseObject_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ReleaseObject_Response_

// alias to use template instance with default allocator
using ReleaseObject_Response =
  go2_apportation_msgs::srv::ReleaseObject_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace go2_apportation_msgs

namespace go2_apportation_msgs
{

namespace srv
{

struct ReleaseObject
{
  using Request = go2_apportation_msgs::srv::ReleaseObject_Request;
  using Response = go2_apportation_msgs::srv::ReleaseObject_Response;
};

}  // namespace srv

}  // namespace go2_apportation_msgs

#endif  // GO2_APPORTATION_MSGS__SRV__DETAIL__RELEASE_OBJECT__STRUCT_HPP_
