// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from go2_apportation_msgs:msg/ThrowStatus.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__FUNCTIONS_H_
#define GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "go2_apportation_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "go2_apportation_msgs/msg/detail/throw_status__struct.h"

/// Initialize msg/ThrowStatus message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__msg__ThrowStatus
 * )) before or use
 * go2_apportation_msgs__msg__ThrowStatus__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__msg__ThrowStatus__init(go2_apportation_msgs__msg__ThrowStatus * msg);

/// Finalize msg/ThrowStatus message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__msg__ThrowStatus__fini(go2_apportation_msgs__msg__ThrowStatus * msg);

/// Create msg/ThrowStatus message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__msg__ThrowStatus__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__msg__ThrowStatus *
go2_apportation_msgs__msg__ThrowStatus__create();

/// Destroy msg/ThrowStatus message.
/**
 * It calls
 * go2_apportation_msgs__msg__ThrowStatus__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__msg__ThrowStatus__destroy(go2_apportation_msgs__msg__ThrowStatus * msg);

/// Check for msg/ThrowStatus message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__msg__ThrowStatus__are_equal(const go2_apportation_msgs__msg__ThrowStatus * lhs, const go2_apportation_msgs__msg__ThrowStatus * rhs);

/// Copy a msg/ThrowStatus message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__msg__ThrowStatus__copy(
  const go2_apportation_msgs__msg__ThrowStatus * input,
  go2_apportation_msgs__msg__ThrowStatus * output);

/// Initialize array of msg/ThrowStatus messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__msg__ThrowStatus__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__msg__ThrowStatus__Sequence__init(go2_apportation_msgs__msg__ThrowStatus__Sequence * array, size_t size);

/// Finalize array of msg/ThrowStatus messages.
/**
 * It calls
 * go2_apportation_msgs__msg__ThrowStatus__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__msg__ThrowStatus__Sequence__fini(go2_apportation_msgs__msg__ThrowStatus__Sequence * array);

/// Create array of msg/ThrowStatus messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__msg__ThrowStatus__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__msg__ThrowStatus__Sequence *
go2_apportation_msgs__msg__ThrowStatus__Sequence__create(size_t size);

/// Destroy array of msg/ThrowStatus messages.
/**
 * It calls
 * go2_apportation_msgs__msg__ThrowStatus__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__msg__ThrowStatus__Sequence__destroy(go2_apportation_msgs__msg__ThrowStatus__Sequence * array);

/// Check for msg/ThrowStatus message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__msg__ThrowStatus__Sequence__are_equal(const go2_apportation_msgs__msg__ThrowStatus__Sequence * lhs, const go2_apportation_msgs__msg__ThrowStatus__Sequence * rhs);

/// Copy an array of msg/ThrowStatus messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__msg__ThrowStatus__Sequence__copy(
  const go2_apportation_msgs__msg__ThrowStatus__Sequence * input,
  go2_apportation_msgs__msg__ThrowStatus__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__MSG__DETAIL__THROW_STATUS__FUNCTIONS_H_
