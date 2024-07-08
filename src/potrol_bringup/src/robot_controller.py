#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import numpy as np

class AckermannController(Node):
    def __init__(self):
        super().__init__('ackermann_controller')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        
        # Robot parameters
        self.wheelbase = self.declare_parameter('wheelbase', 0.472337).get_parameter_value().double_value  # distance between front and rear axles
        self.track_width = self.declare_parameter('track_width', 0.34033).get_parameter_value().double_value  # distance between left and right wheels
        self.wheel_radius = self.declare_parameter('wheel_radius', 0.075).get_parameter_value().double_value  # radius of the wheels
        
        # Publishers for wheel angles and velocities
        self.position_controller_pub = self.create_publisher(Float64MultiArray, '/position_controller/commands', 10)
        self.velocity_controller_pub = self.create_publisher(Float64MultiArray, '/velocity_controller/commands', 10)
        
        self.get_logger().info('Ackermann controller node started')

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
        
        # Publish the angles to the position controller topic
        position_controller_msg = Float64MultiArray()
        position_controller_msg.data = [inner_wheel_angle, outer_wheel_angle]
        self.position_controller_pub.publish(position_controller_msg)
        
        # Publish the speeds to the velocity controller topic
        velocity_controller_msg = Float64MultiArray()
        velocity_controller_msg.data = [wheel_speed, wheel_speed, wheel_speed, wheel_speed]
        self.velocity_controller_pub.publish(velocity_controller_msg)

def main(args=None):
    rclpy.init(args=args)
    ackermann_controller = AckermannController()
    rclpy.spin(ackermann_controller)
    ackermann_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
