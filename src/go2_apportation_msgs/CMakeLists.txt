cmake_minimum_required(VERSION 3.8)
project(go2_apportation_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Detection3D.msg"
  "msg/Detection3DArray.msg"
  "msg/ObjectState.msg"
  "msg/PredictedRegion.msg"
  "msg/InterceptGoal.msg"
  "msg/TrackingDirective.msg"
  "msg/ThrowStatus.msg"
  "action/PickObject.action"
  "srv/ReleaseObject.srv"
  DEPENDENCIES builtin_interfaces geometry_msgs std_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
