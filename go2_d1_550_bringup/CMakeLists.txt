cmake_minimum_required(VERSION 3.8)
project(go2_d1_550_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch scripts
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/d1_550_sdk_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
