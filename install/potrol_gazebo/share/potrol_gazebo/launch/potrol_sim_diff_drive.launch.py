#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory, get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_prefix
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import OpaqueFunction
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition, UnlessCondition
from launch.actions import TimerAction


def launch_setup(context, *args, **kwargs):

    entity_name = LaunchConfiguration('robot_name').perform(context)
    x_spawn = LaunchConfiguration('x_spawn').perform(context)
    y_spawn = LaunchConfiguration('y_spawn').perform(context)
    z_spawn = LaunchConfiguration('z_spawn').perform(context)
    roll_spawn = LaunchConfiguration('roll_spawn').perform(context)
    pitch_spawn = LaunchConfiguration('pitch_spawn').perform(context)
    yaw_spawn = LaunchConfiguration('yaw_spawn').perform(context)

    # Position and orientation
    # [X, Y, Z]
    position = [x_spawn, y_spawn, z_spawn]
    # [Roll, Pitch, Yaw]
    orientation = [roll_spawn, pitch_spawn, yaw_spawn]
    robot_description_topic_name = "/robot_description" # "/" + entity_name + "_robot_description"
    robot_state_publisher_name= entity_name + "_robot_state_publisher"

    # Spawn ROBOT Set Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='potrol_spawn_entity',
        output='screen',
        emulate_tty=True,
        arguments=['-entity',
                   entity_name,
                   '-x', str(position[0]), '-y', str(position[1]
                                                     ), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]
                                                        ), '-Y', str(orientation[2]),
                   '-topic', robot_description_topic_name
                   ],
       
    )


    return [spawn_robot]

def generate_launch_description():

    pkg_potrol_gazebo = get_package_share_directory('potrol_gazebo')
    pkg_potrol_description = get_package_share_directory('potrol_description_cmake')
    pkg_potrol_bringup = get_package_share_directory('potrol_bringup')

    portol_description_path = get_package_share_path('potrol_description_cmake')
    urdf_tutorial_path = get_package_share_path('urdf_tutorial')
    
    default_model_path = portol_description_path / 'urdf/potrol.xacro'
    default_rviz_config_path = portol_description_path / 'rviz/urdf.rviz'
    # default_rviz_config_path = urdf_tutorial_path / 'rviz/urdf.rviz'
    
    gui_arg = DeclareLaunchArgument(name='gui', default_value='false', choices=['true', 'false'],
                                    description='Flag to enable joint_state_publisher_gui')
    model_arg = DeclareLaunchArgument(name='model', default_value=str(default_model_path),
                                      description='Absolute path to robot urdf file')
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=str(default_rviz_config_path),
                                     description='Absolute path to rviz config file')

    gazebo_start_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_potrol_gazebo, 'launch', 'start_world.launch.py'),
        )
    )


    # robot_description = ParameterValue(Command(['xacro ', LaunchConfiguration('model')]),
    #                                    value_type=str)

    # robot_state_publisher_node = Node(
    #     package='robot_state_publisher',
    #     executable='robot_state_publisher',
    #     parameters=[{'robot_description': robot_description}]
    # )

    # # Depending on gui parameter, either launch joint_state_publisher or joint_state_publisher_gui
    # joint_state_publisher_node = Node(
    #     package='joint_state_publisher',
    #     executable='joint_state_publisher',
    #     condition=UnlessCondition(LaunchConfiguration('gui'))
    # )

    # joint_state_publisher_gui_node = Node(
    #     package='joint_state_publisher_gui',
    #     executable='joint_state_publisher_gui',
    #     condition=IfCondition(LaunchConfiguration('gui'))
    # )

    # rviz_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     output='screen',
    #     arguments=['-d', LaunchConfiguration('rvizconfig')],
    # )
    
    
    
    state_joint = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_potrol_description, 'launch', 'state_joint_publisers_diff_drive.launch.py'),
        )
    )

    controller_spawner = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_potrol_bringup, 'launch', 'controller_diff_drive.launch.py'),
        )
    )

    robot_name_arg = DeclareLaunchArgument('robot_name', default_value='potrol')
    x_spawn_arg = DeclareLaunchArgument('x_spawn', default_value='-88.306301')
    y_spawn_arg = DeclareLaunchArgument('y_spawn', default_value='-11.997259')
    z_spawn_arg = DeclareLaunchArgument('z_spawn', default_value='0.659707')
    roll_spawn_arg = DeclareLaunchArgument('roll_spawn', default_value='0.0')
    pitch_spawn_arg = DeclareLaunchArgument('pitch_spawn', default_value='0.0')
    yaw_spawn_arg = DeclareLaunchArgument('yaw_spawn', default_value='1.57')
    
    
    return LaunchDescription([
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=gazebo_start_world,
        #         on_exit=[state_joint],
        #     )
        # ),
        # gazebo_start_world,
        # gui_arg,
        # model_arg,
        # rviz_arg,
        # joint_state_publisher_node,
        # joint_state_publisher_gui_node,
        # robot_state_publisher_node,
        # rviz_node

        robot_name_arg,
        x_spawn_arg,
        y_spawn_arg, 
        z_spawn_arg,
        roll_spawn_arg,
        pitch_spawn_arg,
        yaw_spawn_arg,
        
        OpaqueFunction(function = launch_setup),
        state_joint,
        TimerAction(
            period=5.0,
            actions=[controller_spawner]
        ),
        
    ])