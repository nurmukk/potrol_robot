#!/usr/bin/env python3

# напииши автор 

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from sensor_msgs.msg import JointState
import tf2_ros
import math
import tf2_py
import tf2_ros
import tf2
import tf2_geometry_msgs


class OdomToTfNode(Node):
    def __init__(self):
        super().__init__('odom_to_tf_node')
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.odom_publisher = self.create_publisher(
            Odometry,
            'odom',
            10
        )
        self.joint_state_subscriber = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10
        )
        self.last_time = self.get_clock().now().to_msg()
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.wheel_track = 0.36  # Width between left and right wheels
        self.axle_track = 0.47  # Width between front and rear axles
        self.wheel_radius = 0.11  # Radius of the wheels
        self.prev_wheel_positions = [0.0, 0.0, 0.0, 0.0]  # assuming four wheels

    def joint_state_callback(self, msg):
        wheel_names = ['wheel_forward_left_joint', 'wheel_forward_right_joint', 'wheel_backward_left_joint', 'wheel_backward_right_joint']
        wheel_positions = []

        for wheel_name in wheel_names:
            wheel_index = msg.name.index(wheel_name)
            wheel_positions.append(msg.position[wheel_index])

        wheel_deltas = [wheel_position - prev_wheel_position for wheel_position, prev_wheel_position in zip(wheel_positions, self.prev_wheel_positions)]

        # Calculate dt
        current_time = self.get_clock().now().to_msg()
        dt = (current_time.sec - self.last_time.sec) + (current_time.nanosec - self.last_time.nanosec) / 1e9

        linear_velocity = (sum(wheel_deltas) / len(wheel_deltas)) / dt
        angular_velocity = (wheel_deltas[1] + wheel_deltas[0] - wheel_deltas[3] - wheel_deltas[2]) / (2 * self.wheel_track)

        # Update theta based on angular velocity
        self.theta += angular_velocity * dt

        # Calculate odometry
        delta_x = linear_velocity * math.cos(self.theta) * dt
        delta_y = linear_velocity * math.sin(self.theta) * dt

        self.x += delta_x
        self.y += delta_y

        # Convert theta to quaternion
        # quaternion = tf2_py.transformations.quaternion_from_euler(0, 0, self.theta)
        quaternion = tf2.transformations.quaternion_from_euler(0, 0, self.theta)


        # Publish odometry message
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        odom_msg.pose.pose.orientation.x = quaternion[0]
        odom_msg.pose.pose.orientation.y = quaternion[1]
        odom_msg.pose.pose.orientation.z = quaternion[2]
        odom_msg.pose.pose.orientation.w = quaternion[3]
        self.odom_publisher.publish(odom_msg)

        # Broadcast transform
        transform = TransformStamped()
        transform.header.stamp = current_time
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_footprint'
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0
        transform.transform.rotation.x = quaternion[0]
        transform.transform.rotation.y = quaternion[1]
        transform.transform.rotation.z = quaternion[2]
        transform.transform.rotation.w = quaternion[3]
        self.tf_broadcaster.sendTransform(transform)

        # Update previous wheel positions and time
        self.prev_wheel_positions = wheel_positions
        self.last_time = current_time


def main(args=None):
    rclpy.init(args=args)
    odom_to_tf_node = OdomToTfNode()
    rclpy.spin(odom_to_tf_node)
    odom_to_tf_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    