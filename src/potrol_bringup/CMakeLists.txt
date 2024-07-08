cmake_minimum_required(VERSION 3.5)
project(potrol_bringup)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(xacro REQUIRED)
find_package(urdf REQUIRED)
find_package(robot_state_publisher REQUIRED)
# Find packages
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)

# Add include directories
include_directories(
    include
    ${rclcpp_INCLUDE_DIRS}
    ${nav_msgs_INCLUDE_DIRS}
    ${sensor_msgs_INCLUDE_DIRS}
    ${geometry_msgs_INCLUDE_DIRS}
    ${tf2_INCLUDE_DIRS}
    ${tf2_ros_INCLUDE_DIRS}
)

# Add executable
# add_executable(odom src/odom.cpp)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # uncomment the line when a copyright and license is not present in all source files
  #set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # uncomment the line when this package is not in a git repo
  #set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Link executable with required libraries
# ament_target_dependencies(${PROJECT_NAME}
#     rclcpp
#     nav_msgs
#     sensor_msgs
#     geometry_msgs
#     tf2
#     tf2_ros
# )

# Install executable
# install(TARGETS ${PROJECT_NAME}
#     DESTINATION lib/${PROJECT_NAME}
# )

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME})

install(
  PROGRAMS
  src/robot_controller.py
  src/robot_controller_gpt.py
  
  launch/controller.launch.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
