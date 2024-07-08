#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.h"
#include <math.h>
#include <vector>

class OdomToTfNode : public rclcpp::Node
{
public:
    OdomToTfNode() : Node("odom_to_tf_node")
    {
        tf_broadcaster = std::make_shared<tf2_ros::TransformBroadcaster>(this);
        odom_publisher = this->create_publisher<nav_msgs::msg::Odometry>("odom", 10);
        joint_state_subscriber = this->create_subscription<sensor_msgs::msg::JointState>(
            "joint_states", 10, std::bind(&OdomToTfNode::joint_state_callback, this, std::placeholders::_1));

        last_time = this->now();
        x = 0.0;
        y = 0.0;
        theta = 0.0;
        wheel_track = 0.36;  // Width between left and right wheels
        axle_track = 0.47;   // Width between front and rear axles
        wheel_radius = 0.11; // Radius of the wheels
        prev_wheel_positions = {0.0, 0.0, 0.0, 0.0}; // assuming four wheels
    }

private:
    void joint_state_callback(const sensor_msgs::msg::JointState::SharedPtr msg)
    {
        std::vector<std::string> wheel_names = {"wheel_forward_left_joint", "wheel_forward_right_joint", "wheel_backward_left_joint", "wheel_backward_right_joint"};
        std::vector<double> wheel_positions;

        for (const auto &wheel_name : wheel_names)
        {
            auto it = std::find(msg->name.begin(), msg->name.end(), wheel_name);
            if (it != msg->name.end())
            {
                int wheel_index = std::distance(msg->name.begin(), it);
                wheel_positions.push_back(msg->position[wheel_index]);
            }
        }

        std::vector<double> wheel_deltas;
        for (size_t i = 0; i < wheel_positions.size(); ++i)
        {
            wheel_deltas.push_back(wheel_positions[i] - prev_wheel_positions[i]);
        }

        // Calculate dt
        auto current_time = this->now();
        double dt = (current_time - last_time).seconds();

        double linear_velocity = (std::accumulate(wheel_deltas.begin(), wheel_deltas.end(), 0.0) / wheel_deltas.size()) / dt;
        double angular_velocity = (wheel_deltas[1] + wheel_deltas[0] - wheel_deltas[3] - wheel_deltas[2]) / (2 * wheel_track);

        // Update theta based on angular velocity
        theta += angular_velocity * dt;

        // Calculate odometry
        double delta_x = linear_velocity * cos(theta) * dt;
        double delta_y = linear_velocity * sin(theta) * dt;

        x += delta_x;
        y += delta_y;

        // Convert theta to quaternion
        tf2::Quaternion quaternion;
        quaternion.setRPY(0, 0, theta);

        // Publish odometry message
        auto odom_msg = nav_msgs::msg::Odometry();
        odom_msg.header.stamp = current_time;
        odom_msg.header.frame_id = "odom";
        odom_msg.child_frame_id = "base_footprint";
        odom_msg.pose.pose.position.x = x;
        odom_msg.pose.pose.position.y = y;
        odom_msg.pose.pose.position.z = 0.0;
        tf2::convert(quaternion, odom_msg.pose.pose.orientation);
        odom_publisher->publish(odom_msg);

        // Broadcast transform
        auto transform = geometry_msgs::msg::TransformStamped();
        transform.header.stamp = current_time;
        transform.header.frame_id = "odom";
        transform.child_frame_id = "base_footprint";
        transform.transform.translation.x = x;
        transform.transform.translation.y = y;
        transform.transform.translation.z = 0.0;
        tf2::convert(quaternion, transform.transform.rotation);
        tf_broadcaster->sendTransform(transform);

        // Update previous wheel positions and time
        prev_wheel_positions = wheel_positions;
        last_time = current_time;
    }

    rclcpp::Time last_time;
    double x, y, theta, wheel_track, axle_track, wheel_radius;
    std::vector<double> prev_wheel_positions;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_publisher;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_subscriber;
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto odom_to_tf_node = std::make_shared<OdomToTfNode>();
    rclcpp::spin(odom_to_tf_node);
    rclcpp::shutdown();
    return 0;
}
