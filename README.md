# Patrol Robot

A ROS-based patrol robot designed for autonomous navigation and surveillance tasks within indoor environments. This project utilizes ROS2, Gazebo, and computer vision algorithms for real-time object detection and localization.
###Description

The Patrol Robot is an autonomous mobile robot equipped with sensors and cameras to patrol designated areas. It can navigate through predefined waypoints, avoid obstacles, and detect objects of interest such as trash or intruders. The robot's capabilities include:

    Autonomous navigation using ROS2 and the Navigation2 (nav2) package.
    Simultaneous Localization and Mapping (SLAM) for environment mapping.
    Object detection using the YOLOv8 model on repository link_to_rep 
    Integration with Gazebo for simulation and testing. 

###Installation
####Prerequisites

Ensure you have the following installed on your system:

    Ubuntu 22.04 
    ROS2 Humble


###Launch the project

#####Launch Gazebo simulation
```
ros2 launch potrol_gazebo empty_world.launch.py
```
_If you need other worlds, look for them in the directory_
#####Launch robot with diff_drive_controller 
```
ros2 launch potrol_gazebo potrol_sim_diff_drive.launch.py
```

#####Launch robot with Ackermann_controller
```
ros2 launch potrol_gazebo potrol_sim_ackermann.launch.py
```