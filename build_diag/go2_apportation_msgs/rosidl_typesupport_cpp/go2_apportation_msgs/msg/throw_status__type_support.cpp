// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from go2_apportation_msgs:msg/ThrowStatus.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "go2_apportation_msgs/msg/detail/throw_status__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace go2_apportation_msgs
{

namespace msg
{

namespace rosidl_typesupport_cpp
{

typedef struct _ThrowStatus_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ThrowStatus_type_support_ids_t;

static const _ThrowStatus_type_support_ids_t _ThrowStatus_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ThrowStatus_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ThrowStatus_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ThrowStatus_type_support_symbol_names_t _ThrowStatus_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, go2_apportation_msgs, msg, ThrowStatus)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, go2_apportation_msgs, msg, ThrowStatus)),
  }
};

typedef struct _ThrowStatus_type_support_data_t
{
  void * data[2];
} _ThrowStatus_type_support_data_t;

static _ThrowStatus_type_support_data_t _ThrowStatus_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ThrowStatus_message_typesupport_map = {
  2,
  "go2_apportation_msgs",
  &_ThrowStatus_message_typesupport_ids.typesupport_identifier[0],
  &_ThrowStatus_message_typesupport_symbol_names.symbol_name[0],
  &_ThrowStatus_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ThrowStatus_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ThrowStatus_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace msg

}  // namespace go2_apportation_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<go2_apportation_msgs::msg::ThrowStatus>()
{
  return &::go2_apportation_msgs::msg::rosidl_typesupport_cpp::ThrowStatus_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, go2_apportation_msgs, msg, ThrowStatus)() {
  return get_message_type_support_handle<go2_apportation_msgs::msg::ThrowStatus>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp
