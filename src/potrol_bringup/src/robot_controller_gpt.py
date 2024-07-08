#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist, TransformStamped
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import numpy as np
import math
from tf_transformations import quaternion_from_euler
from rclpy.time import Time
from rclpy.constants import S_TO_NS

class AckermannController(Node):
    def __init__(self):
        super().__init__('ackermann_controller')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.joint_sub_ = self.create_subscription(JointState, "joint_states", self.joint_callback, 10)
        self.odom_pub_ = self.create_publisher(Odometry, "odom", 10)

        self.wheelbase = self.declare_parameter('wheelbase', 0.472337).get_parameter_value().double_value  # distance between front and rear axles
        self.track_width = self.declare_parameter('track_width', 0.34033).get_parameter_value().double_value  # distance between left and right wheels
        self.wheel_radius = self.declare_parameter('wheel_radius', 0.075).get_parameter_value().double_value  # radius of the wheels

        self.position_controller_pub = self.create_publisher(Float64MultiArray, '/position_controller/commands', 10)
        self.velocity_controller_pub = self.create_publisher(Float64MultiArray, '/velocity_controller/commands', 10)

        self.get_logger().info('Ackermann controller node started')

        self.left_wheel_prev_pos_ = 0.0
        self.right_wheel_prev_pos_ = 0.0
        self.x_ = 0.0
        self.y_ = 0.0
        self.theta_ = 0.0

        self.odom_msg_ = Odometry()
        self.odom_msg_.header.frame_id = "odom"
        self.odom_msg_.child_frame_id = "base_footprint"
        self.odom_msg_.pose.pose.orientation.x = 0.0
        self.odom_msg_.pose.pose.orientation.y = 0.0
        self.odom_msg_.pose.pose.orientation.z = 0.0
        self.odom_msg_.pose.pose.orientation.w = 1.0

        self.br_ = TransformBroadcaster(self)
        self.transform_stamped_ = TransformStamped()
        self.transform_stamped_.header.frame_id = "odom"
        self.transform_stamped_.child_frame_id = "base_footprint"

        self.prev_time_ = self.get_clock().now()

    def listener_callback(self, msg):
        linear_velocity = msg.linear.x
        angular_velocity = msg.angular.z

        if angular_velocity != 0:
            radius = linear_velocity / angular_velocity
            inner_wheel_angle = np.arctan(self.wheelbase / (radius - self.track_width / 2))
            outer_wheel_angle = np.arctan(self.wheelbase / (radius + self.track_width / 2))
        else:
            inner_wheel_angle = 0.0
            outer_wheel_angle = 0.0

        wheel_speed = linear_velocity / self.wheel_radius

        self.get_logger().info(f'Inner wheel angle: {inner_wheel_angle}, Outer wheel angle: {outer_wheel_angle}')
        self.get_logger().info(f'Wheel speed: {wheel_speed}')

        position_controller_msg = Float64MultiArray()
        position_controller_msg.data = [inner_wheel_angle, outer_wheel_angle]
        self.position_controller_pub.publish(position_controller_msg)

        velocity_controller_msg = Float64MultiArray()
        velocity_controller_msg.data = [wheel_speed, wheel_speed, wheel_speed, wheel_speed]
        self.velocity_controller_pub.publish(velocity_controller_msg)

    def joint_callback(self, msg):
        dp_left = msg.position[1] - self.left_wheel_prev_pos_
        dp_right = msg.position[0] - self.right_wheel_prev_pos_
        dt = Time.from_msg(msg.header.stamp) - self.prev_time_

        self.left_wheel_prev_pos_ = msg.position[1]
        self.right_wheel_prev_pos_ = msg.position[0]
        self.prev_time_ = Time.from_msg(msg.header.stamp)

        if dt.nanoseconds == 0:
            return

        fi_left = dp_left / (dt.nanoseconds / S_TO_NS)
        fi_right = dp_right / (dt.nanoseconds / S_TO_NS)

        linear = (self.wheel_radius * fi_right + self.wheel_radius * fi_left) / 2
        angular = (self.wheel_radius * fi_right - self.wheel_radius * fi_left) / self.track_width

        d_s = (self.wheel_radius * dp_right + self.wheel_radius * dp_left) / 2
        d_theta = (self.wheel_radius * dp_right - self.wheel_radius * dp_left) / self.track_width
        self.theta_ += d_theta
        self.x_ += d_s * math.cos(self.theta_)
        self.y_ += d_s * math.sin(self.theta_)

        q = quaternion_from_euler(0, 0, self.theta_)
        current_time = self.get_clock().now()

        self.odom_msg_.header.stamp = current_time.to_msg()
        self.odom_msg_.pose.pose.position.x = self.x_
        self.odom_msg_.pose.pose.position.y = self.y_
        self.odom_msg_.pose.pose.orientation.x = q[0]
        self.odom_msg_.pose.pose.orientation.y = q[1]
        self.odom_msg_.pose.pose.orientation.z = q[2]
        self.odom_msg_.pose.pose.orientation.w = q[3]
        self.odom_msg_.twist.twist.linear.x = linear
        self.odom_msg_.twist.twist.angular.z = angular
        self.odom_pub_.publish(self.odom_msg_)

        self.transform_stamped_.header.stamp = current_time.to_msg()
        self.transform_stamped_.transform.translation.x = self.x_
        self.transform_stamped_.transform.translation.y = self.y_
        self.transform_stamped_.transform.translation.z = 0.0
        self.transform_stamped_.transform.rotation.x = q[0]
        self.transform_stamped_.transform.rotation.y = q[1]
        self.transform_stamped_.transform.rotation.z = q[2]
        self.transform_stamped_.transform.rotation.w = q[3]
        self.br_.sendTransform(self.transform_stamped_)


def main(args=None):
    rclpy.init(args=args)
    ackermann_controller = AckermannController()
    rclpy.spin(ackermann_controller)
    ackermann_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
