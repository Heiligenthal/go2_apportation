// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from go2_apportation_msgs:srv/ReleaseObject.idl
// generated code does not contain a copyright notice
#include "go2_apportation_msgs/srv/detail/release_object__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
go2_apportation_msgs__srv__ReleaseObject_Request__init(go2_apportation_msgs__srv__ReleaseObject_Request * msg)
{
  if (!msg) {
    return false;
  }
  // release_mode
  // verify_open
  return true;
}

void
go2_apportation_msgs__srv__ReleaseObject_Request__fini(go2_apportation_msgs__srv__ReleaseObject_Request * msg)
{
  if (!msg) {
    return;
  }
  // release_mode
  // verify_open
}

bool
go2_apportation_msgs__srv__ReleaseObject_Request__are_equal(const go2_apportation_msgs__srv__ReleaseObject_Request * lhs, const go2_apportation_msgs__srv__ReleaseObject_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // release_mode
  if (lhs->release_mode != rhs->release_mode) {
    return false;
  }
  // verify_open
  if (lhs->verify_open != rhs->verify_open) {
    return false;
  }
  return true;
}

bool
go2_apportation_msgs__srv__ReleaseObject_Request__copy(
  const go2_apportation_msgs__srv__ReleaseObject_Request * input,
  go2_apportation_msgs__srv__ReleaseObject_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // release_mode
  output->release_mode = input->release_mode;
  // verify_open
  output->verify_open = input->verify_open;
  return true;
}

go2_apportation_msgs__srv__ReleaseObject_Request *
go2_apportation_msgs__srv__ReleaseObject_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__srv__ReleaseObject_Request * msg = (go2_apportation_msgs__srv__ReleaseObject_Request *)allocator.allocate(sizeof(go2_apportation_msgs__srv__ReleaseObject_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(go2_apportation_msgs__srv__ReleaseObject_Request));
  bool success = go2_apportation_msgs__srv__ReleaseObject_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
go2_apportation_msgs__srv__ReleaseObject_Request__destroy(go2_apportation_msgs__srv__ReleaseObject_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    go2_apportation_msgs__srv__ReleaseObject_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__init(go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__srv__ReleaseObject_Request * data = NULL;

  if (size) {
    data = (go2_apportation_msgs__srv__ReleaseObject_Request *)allocator.zero_allocate(size, sizeof(go2_apportation_msgs__srv__ReleaseObject_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = go2_apportation_msgs__srv__ReleaseObject_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        go2_apportation_msgs__srv__ReleaseObject_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__fini(go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      go2_apportation_msgs__srv__ReleaseObject_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

go2_apportation_msgs__srv__ReleaseObject_Request__Sequence *
go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * array = (go2_apportation_msgs__srv__ReleaseObject_Request__Sequence *)allocator.allocate(sizeof(go2_apportation_msgs__srv__ReleaseObject_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__destroy(go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__are_equal(const go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * lhs, const go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!go2_apportation_msgs__srv__ReleaseObject_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
go2_apportation_msgs__srv__ReleaseObject_Request__Sequence__copy(
  const go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * input,
  go2_apportation_msgs__srv__ReleaseObject_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(go2_apportation_msgs__srv__ReleaseObject_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    go2_apportation_msgs__srv__ReleaseObject_Request * data =
      (go2_apportation_msgs__srv__ReleaseObject_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!go2_apportation_msgs__srv__ReleaseObject_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          go2_apportation_msgs__srv__ReleaseObject_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!go2_apportation_msgs__srv__ReleaseObject_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
go2_apportation_msgs__srv__ReleaseObject_Response__init(go2_apportation_msgs__srv__ReleaseObject_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // result_code
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    go2_apportation_msgs__srv__ReleaseObject_Response__fini(msg);
    return false;
  }
  return true;
}

void
go2_apportation_msgs__srv__ReleaseObject_Response__fini(go2_apportation_msgs__srv__ReleaseObject_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // result_code
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
go2_apportation_msgs__srv__ReleaseObject_Response__are_equal(const go2_apportation_msgs__srv__ReleaseObject_Response * lhs, const go2_apportation_msgs__srv__ReleaseObject_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // result_code
  if (lhs->result_code != rhs->result_code) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
go2_apportation_msgs__srv__ReleaseObject_Response__copy(
  const go2_apportation_msgs__srv__ReleaseObject_Response * input,
  go2_apportation_msgs__srv__ReleaseObject_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // result_code
  output->result_code = input->result_code;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

go2_apportation_msgs__srv__ReleaseObject_Response *
go2_apportation_msgs__srv__ReleaseObject_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__srv__ReleaseObject_Response * msg = (go2_apportation_msgs__srv__ReleaseObject_Response *)allocator.allocate(sizeof(go2_apportation_msgs__srv__ReleaseObject_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(go2_apportation_msgs__srv__ReleaseObject_Response));
  bool success = go2_apportation_msgs__srv__ReleaseObject_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
go2_apportation_msgs__srv__ReleaseObject_Response__destroy(go2_apportation_msgs__srv__ReleaseObject_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    go2_apportation_msgs__srv__ReleaseObject_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__init(go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__srv__ReleaseObject_Response * data = NULL;

  if (size) {
    data = (go2_apportation_msgs__srv__ReleaseObject_Response *)allocator.zero_allocate(size, sizeof(go2_apportation_msgs__srv__ReleaseObject_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = go2_apportation_msgs__srv__ReleaseObject_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        go2_apportation_msgs__srv__ReleaseObject_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__fini(go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      go2_apportation_msgs__srv__ReleaseObject_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

go2_apportation_msgs__srv__ReleaseObject_Response__Sequence *
go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * array = (go2_apportation_msgs__srv__ReleaseObject_Response__Sequence *)allocator.allocate(sizeof(go2_apportation_msgs__srv__ReleaseObject_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__destroy(go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__are_equal(const go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * lhs, const go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!go2_apportation_msgs__srv__ReleaseObject_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
go2_apportation_msgs__srv__ReleaseObject_Response__Sequence__copy(
  const go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * input,
  go2_apportation_msgs__srv__ReleaseObject_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(go2_apportation_msgs__srv__ReleaseObject_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    go2_apportation_msgs__srv__ReleaseObject_Response * data =
      (go2_apportation_msgs__srv__ReleaseObject_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!go2_apportation_msgs__srv__ReleaseObject_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          go2_apportation_msgs__srv__ReleaseObject_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!go2_apportation_msgs__srv__ReleaseObject_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
