import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


class OmniKinematics(Node):

    def __init__(self):
        super().__init__('omni_kinematics')

        # ---- Robot parameters (EDIT THESE if needed) ----
        self.r = 0.016      # wheel radius (meters)
        self.L = 0.072      # distance from center to wheel (meters)

        # Wheel angles (radians)
        self.theta_left  = math.radians(150.0)
        self.theta_right = math.radians(30.0)
        self.theta_back  = math.radians(270.0)

        # Subscriber
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        # Publisher
        self.pub = self.create_publisher(
            Float64MultiArray,
            '/forward_velocity_controller/commands',
            10
        )

    def compute_wheel_velocity(self, vx, vy, omega, theta):
        return (-math.sin(theta) * vx +
                math.cos(theta) * vy +
                self.L * omega) / self.r

    def cmd_callback(self, msg):
        vx = msg.linear.x
        vy = msg.linear.y
        omega = msg.angular.z

        w_left = self.compute_wheel_velocity(vx, vy, omega, self.theta_left)
        w_right = self.compute_wheel_velocity(vx, vy, omega, self.theta_right)
        w_back = self.compute_wheel_velocity(vx, vy, omega, self.theta_back)

        out = Float64MultiArray()
        out.data = [w_left, w_right, w_back]

        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = OmniKinematics()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()