import os 

from launch_ros.actions import Node
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch import LaunchDescription
# from ament_index_python.packages import get_package_share_path



def generate_launch_description():

    
    # portol_description_path = get_package_share_path('potrol_description_cmake')



    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    diff_drive = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont", "--controller-manager", "/controller_manager"],
        # remappings=[('/diff_cont/cmd_vel', 'cmd_vel')]
    )

    # robot_controller_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_trajectory_controller", "-c", "/controller_manager"],
    # )

    # velocity_controller_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_velocity_controller", "-c", "/controller_manager"],
    # )

    

    return LaunchDescription([
        joint_state_broadcaster_spawner,
        diff_drive
                
    ])