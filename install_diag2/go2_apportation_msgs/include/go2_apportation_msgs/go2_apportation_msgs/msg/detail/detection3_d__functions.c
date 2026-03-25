// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from go2_apportation_msgs:msg/Detection3D.idl
// generated code does not contain a copyright notice
#include "go2_apportation_msgs/msg/detail/detection3_d__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `pose`
#include "geometry_msgs/msg/detail/pose_with_covariance__functions.h"

bool
go2_apportation_msgs__msg__Detection3D__init(go2_apportation_msgs__msg__Detection3D * msg)
{
  if (!msg) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseWithCovariance__init(&msg->pose)) {
    go2_apportation_msgs__msg__Detection3D__fini(msg);
    return false;
  }
  // confidence
  // class_id
  return true;
}

void
go2_apportation_msgs__msg__Detection3D__fini(go2_apportation_msgs__msg__Detection3D * msg)
{
  if (!msg) {
    return;
  }
  // pose
  geometry_msgs__msg__PoseWithCovariance__fini(&msg->pose);
  // confidence
  // class_id
}

bool
go2_apportation_msgs__msg__Detection3D__are_equal(const go2_apportation_msgs__msg__Detection3D * lhs, const go2_apportation_msgs__msg__Detection3D * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseWithCovariance__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  // class_id
  if (lhs->class_id != rhs->class_id) {
    return false;
  }
  return true;
}

bool
go2_apportation_msgs__msg__Detection3D__copy(
  const go2_apportation_msgs__msg__Detection3D * input,
  go2_apportation_msgs__msg__Detection3D * output)
{
  if (!input || !output) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseWithCovariance__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  // confidence
  output->confidence = input->confidence;
  // class_id
  output->class_id = input->class_id;
  return true;
}

go2_apportation_msgs__msg__Detection3D *
go2_apportation_msgs__msg__Detection3D__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__msg__Detection3D * msg = (go2_apportation_msgs__msg__Detection3D *)allocator.allocate(sizeof(go2_apportation_msgs__msg__Detection3D), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(go2_apportation_msgs__msg__Detection3D));
  bool success = go2_apportation_msgs__msg__Detection3D__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
go2_apportation_msgs__msg__Detection3D__destroy(go2_apportation_msgs__msg__Detection3D * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    go2_apportation_msgs__msg__Detection3D__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
go2_apportation_msgs__msg__Detection3D__Sequence__init(go2_apportation_msgs__msg__Detection3D__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__msg__Detection3D * data = NULL;

  if (size) {
    data = (go2_apportation_msgs__msg__Detection3D *)allocator.zero_allocate(size, sizeof(go2_apportation_msgs__msg__Detection3D), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = go2_apportation_msgs__msg__Detection3D__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        go2_apportation_msgs__msg__Detection3D__fini(&data[i - 1]);
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
go2_apportation_msgs__msg__Detection3D__Sequence__fini(go2_apportation_msgs__msg__Detection3D__Sequence * array)
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
      go2_apportation_msgs__msg__Detection3D__fini(&array->data[i]);
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

go2_apportation_msgs__msg__Detection3D__Sequence *
go2_apportation_msgs__msg__Detection3D__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  go2_apportation_msgs__msg__Detection3D__Sequence * array = (go2_apportation_msgs__msg__Detection3D__Sequence *)allocator.allocate(sizeof(go2_apportation_msgs__msg__Detection3D__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = go2_apportation_msgs__msg__Detection3D__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
go2_apportation_msgs__msg__Detection3D__Sequence__destroy(go2_apportation_msgs__msg__Detection3D__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    go2_apportation_msgs__msg__Detection3D__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
go2_apportation_msgs__msg__Detection3D__Sequence__are_equal(const go2_apportation_msgs__msg__Detection3D__Sequence * lhs, const go2_apportation_msgs__msg__Detection3D__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!go2_apportation_msgs__msg__Detection3D__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
go2_apportation_msgs__msg__Detection3D__Sequence__copy(
  const go2_apportation_msgs__msg__Detection3D__Sequence * input,
  go2_apportation_msgs__msg__Detection3D__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(go2_apportation_msgs__msg__Detection3D);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    go2_apportation_msgs__msg__Detection3D * data =
      (go2_apportation_msgs__msg__Detection3D *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!go2_apportation_msgs__msg__Detection3D__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          go2_apportation_msgs__msg__Detection3D__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!go2_apportation_msgs__msg__Detection3D__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
