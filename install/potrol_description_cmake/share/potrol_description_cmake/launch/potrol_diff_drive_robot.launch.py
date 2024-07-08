# launch/my_robot.launch.py

import os
from ament_index_python.packages import get_package_share_directory, get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.actions import TimerAction
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_my_robot_description = get_package_share_directory('potrol_description_cmake')
    # pkg_my_robot_control = get_package_share_directory('my_robot_control')

    robot_description_path = os.path.join(pkg_my_robot_description, 'urdf', 'potrol_diff_drive.xacro')

    robot_description = ParameterValue(Command(['xacro ', str(robot_description_path)]),
                                       value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': Command(['xacro ', robot_description])}]
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['diff_cont'],
        output='screen'
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'potrol', '-file', robot_description_path],
        output='screen'
    )

    return LaunchDescription([
        TimerAction(
            period=5.0,
            actions=[spawn_entity]
        ),
        TimerAction(
            period=10.0,
            actions=[robot_state_publisher_node]
        ),
        TimerAction(
            period=15.0,
            actions=[joint_state_broadcaster_spawner]
        ),
        TimerAction(
            period=20.0,
            actions=[diff_drive_controller_spawner]
        ),
    ])
