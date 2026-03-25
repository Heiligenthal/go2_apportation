// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from go2_apportation_msgs:action/PickObject.idl
// generated code does not contain a copyright notice

#ifndef GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__FUNCTIONS_H_
#define GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "go2_apportation_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "go2_apportation_msgs/action/detail/pick_object__struct.h"

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_Goal
 * )) before or use
 * go2_apportation_msgs__action__PickObject_Goal__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Goal__init(go2_apportation_msgs__action__PickObject_Goal * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Goal__fini(go2_apportation_msgs__action__PickObject_Goal * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_Goal__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_Goal *
go2_apportation_msgs__action__PickObject_Goal__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Goal__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Goal__destroy(go2_apportation_msgs__action__PickObject_Goal * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Goal__are_equal(const go2_apportation_msgs__action__PickObject_Goal * lhs, const go2_apportation_msgs__action__PickObject_Goal * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_Goal__copy(
  const go2_apportation_msgs__action__PickObject_Goal * input,
  go2_apportation_msgs__action__PickObject_Goal * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_Goal__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Goal__Sequence__init(go2_apportation_msgs__action__PickObject_Goal__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Goal__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Goal__Sequence__fini(go2_apportation_msgs__action__PickObject_Goal__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_Goal__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_Goal__Sequence *
go2_apportation_msgs__action__PickObject_Goal__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Goal__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Goal__Sequence__destroy(go2_apportation_msgs__action__PickObject_Goal__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Goal__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_Goal__Sequence * lhs, const go2_apportation_msgs__action__PickObject_Goal__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_Goal__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_Goal__Sequence * input,
  go2_apportation_msgs__action__PickObject_Goal__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_Result
 * )) before or use
 * go2_apportation_msgs__action__PickObject_Result__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Result__init(go2_apportation_msgs__action__PickObject_Result * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Result__fini(go2_apportation_msgs__action__PickObject_Result * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_Result__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_Result *
go2_apportation_msgs__action__PickObject_Result__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Result__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Result__destroy(go2_apportation_msgs__action__PickObject_Result * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Result__are_equal(const go2_apportation_msgs__action__PickObject_Result * lhs, const go2_apportation_msgs__action__PickObject_Result * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_Result__copy(
  const go2_apportation_msgs__action__PickObject_Result * input,
  go2_apportation_msgs__action__PickObject_Result * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_Result__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Result__Sequence__init(go2_apportation_msgs__action__PickObject_Result__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Result__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Result__Sequence__fini(go2_apportation_msgs__action__PickObject_Result__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_Result__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_Result__Sequence *
go2_apportation_msgs__action__PickObject_Result__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Result__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Result__Sequence__destroy(go2_apportation_msgs__action__PickObject_Result__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Result__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_Result__Sequence * lhs, const go2_apportation_msgs__action__PickObject_Result__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_Result__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_Result__Sequence * input,
  go2_apportation_msgs__action__PickObject_Result__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_Feedback
 * )) before or use
 * go2_apportation_msgs__action__PickObject_Feedback__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Feedback__init(go2_apportation_msgs__action__PickObject_Feedback * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Feedback__fini(go2_apportation_msgs__action__PickObject_Feedback * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_Feedback__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_Feedback *
go2_apportation_msgs__action__PickObject_Feedback__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Feedback__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Feedback__destroy(go2_apportation_msgs__action__PickObject_Feedback * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Feedback__are_equal(const go2_apportation_msgs__action__PickObject_Feedback * lhs, const go2_apportation_msgs__action__PickObject_Feedback * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_Feedback__copy(
  const go2_apportation_msgs__action__PickObject_Feedback * input,
  go2_apportation_msgs__action__PickObject_Feedback * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_Feedback__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Feedback__Sequence__init(go2_apportation_msgs__action__PickObject_Feedback__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Feedback__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Feedback__Sequence__fini(go2_apportation_msgs__action__PickObject_Feedback__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_Feedback__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_Feedback__Sequence *
go2_apportation_msgs__action__PickObject_Feedback__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_Feedback__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_Feedback__Sequence__destroy(go2_apportation_msgs__action__PickObject_Feedback__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_Feedback__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_Feedback__Sequence * lhs, const go2_apportation_msgs__action__PickObject_Feedback__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_Feedback__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_Feedback__Sequence * input,
  go2_apportation_msgs__action__PickObject_Feedback__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_SendGoal_Request
 * )) before or use
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Request__init(go2_apportation_msgs__action__PickObject_SendGoal_Request * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Request__fini(go2_apportation_msgs__action__PickObject_SendGoal_Request * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_SendGoal_Request *
go2_apportation_msgs__action__PickObject_SendGoal_Request__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Request__destroy(go2_apportation_msgs__action__PickObject_SendGoal_Request * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Request__are_equal(const go2_apportation_msgs__action__PickObject_SendGoal_Request * lhs, const go2_apportation_msgs__action__PickObject_SendGoal_Request * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_SendGoal_Request__copy(
  const go2_apportation_msgs__action__PickObject_SendGoal_Request * input,
  go2_apportation_msgs__action__PickObject_SendGoal_Request * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__init(go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__fini(go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence *
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__destroy(go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * lhs, const go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * input,
  go2_apportation_msgs__action__PickObject_SendGoal_Request__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_SendGoal_Response
 * )) before or use
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Response__init(go2_apportation_msgs__action__PickObject_SendGoal_Response * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Response__fini(go2_apportation_msgs__action__PickObject_SendGoal_Response * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_SendGoal_Response *
go2_apportation_msgs__action__PickObject_SendGoal_Response__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Response__destroy(go2_apportation_msgs__action__PickObject_SendGoal_Response * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Response__are_equal(const go2_apportation_msgs__action__PickObject_SendGoal_Response * lhs, const go2_apportation_msgs__action__PickObject_SendGoal_Response * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_SendGoal_Response__copy(
  const go2_apportation_msgs__action__PickObject_SendGoal_Response * input,
  go2_apportation_msgs__action__PickObject_SendGoal_Response * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__init(go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__fini(go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence *
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__destroy(go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * lhs, const go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * input,
  go2_apportation_msgs__action__PickObject_SendGoal_Response__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_GetResult_Request
 * )) before or use
 * go2_apportation_msgs__action__PickObject_GetResult_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Request__init(go2_apportation_msgs__action__PickObject_GetResult_Request * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Request__fini(go2_apportation_msgs__action__PickObject_GetResult_Request * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_GetResult_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_GetResult_Request *
go2_apportation_msgs__action__PickObject_GetResult_Request__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_GetResult_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Request__destroy(go2_apportation_msgs__action__PickObject_GetResult_Request * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Request__are_equal(const go2_apportation_msgs__action__PickObject_GetResult_Request * lhs, const go2_apportation_msgs__action__PickObject_GetResult_Request * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_GetResult_Request__copy(
  const go2_apportation_msgs__action__PickObject_GetResult_Request * input,
  go2_apportation_msgs__action__PickObject_GetResult_Request * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_GetResult_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__init(go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_GetResult_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__fini(go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence *
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__destroy(go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * lhs, const go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * input,
  go2_apportation_msgs__action__PickObject_GetResult_Request__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_GetResult_Response
 * )) before or use
 * go2_apportation_msgs__action__PickObject_GetResult_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Response__init(go2_apportation_msgs__action__PickObject_GetResult_Response * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Response__fini(go2_apportation_msgs__action__PickObject_GetResult_Response * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_GetResult_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_GetResult_Response *
go2_apportation_msgs__action__PickObject_GetResult_Response__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_GetResult_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Response__destroy(go2_apportation_msgs__action__PickObject_GetResult_Response * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Response__are_equal(const go2_apportation_msgs__action__PickObject_GetResult_Response * lhs, const go2_apportation_msgs__action__PickObject_GetResult_Response * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_GetResult_Response__copy(
  const go2_apportation_msgs__action__PickObject_GetResult_Response * input,
  go2_apportation_msgs__action__PickObject_GetResult_Response * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_GetResult_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__init(go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_GetResult_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__fini(go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence *
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__destroy(go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * lhs, const go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * input,
  go2_apportation_msgs__action__PickObject_GetResult_Response__Sequence * output);

/// Initialize action/PickObject message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * go2_apportation_msgs__action__PickObject_FeedbackMessage
 * )) before or use
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_FeedbackMessage__init(go2_apportation_msgs__action__PickObject_FeedbackMessage * msg);

/// Finalize action/PickObject message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_FeedbackMessage__fini(go2_apportation_msgs__action__PickObject_FeedbackMessage * msg);

/// Create action/PickObject message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_FeedbackMessage *
go2_apportation_msgs__action__PickObject_FeedbackMessage__create();

/// Destroy action/PickObject message.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_FeedbackMessage__destroy(go2_apportation_msgs__action__PickObject_FeedbackMessage * msg);

/// Check for action/PickObject message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_FeedbackMessage__are_equal(const go2_apportation_msgs__action__PickObject_FeedbackMessage * lhs, const go2_apportation_msgs__action__PickObject_FeedbackMessage * rhs);

/// Copy a action/PickObject message.
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
go2_apportation_msgs__action__PickObject_FeedbackMessage__copy(
  const go2_apportation_msgs__action__PickObject_FeedbackMessage * input,
  go2_apportation_msgs__action__PickObject_FeedbackMessage * output);

/// Initialize array of action/PickObject messages.
/**
 * It allocates the memory for the number of elements and calls
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__init(go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * array, size_t size);

/// Finalize array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__fini(go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * array);

/// Create array of action/PickObject messages.
/**
 * It allocates the memory for the array and calls
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence *
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__create(size_t size);

/// Destroy array of action/PickObject messages.
/**
 * It calls
 * go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
void
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__destroy(go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * array);

/// Check for action/PickObject message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_go2_apportation_msgs
bool
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__are_equal(const go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * lhs, const go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * rhs);

/// Copy an array of action/PickObject messages.
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
go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence__copy(
  const go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * input,
  go2_apportation_msgs__action__PickObject_FeedbackMessage__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // GO2_APPORTATION_MSGS__ACTION__DETAIL__PICK_OBJECT__FUNCTIONS_H_
