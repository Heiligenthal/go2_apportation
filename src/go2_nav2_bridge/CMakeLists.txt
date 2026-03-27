cmake_minimum_required(VERSION 3.8)
project(go2_nav2_bridge)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(go2_interfaces REQUIRED)

add_executable(go2_nav2_bridge
  src/go2_nav2_bridge.cpp
  src/ros2_sport_client.cpp
)

target_include_directories(go2_nav2_bridge PRIVATE
  include
)

ament_target_dependencies(go2_nav2_bridge
  geometry_msgs
  nav_msgs
  rclcpp
  std_msgs
  tf2
  tf2_ros
  go2_interfaces
)

install(TARGETS
  go2_nav2_bridge
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(FILES README.md
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
