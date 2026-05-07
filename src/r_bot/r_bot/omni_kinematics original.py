#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


class OmniKinematics(Node):

    def __init__(self):
        super().__init__('omni_kinematics')

        # ================= ROBOT PARAMETERS =================
        # Must match URDF
        self.r = 0.03      # wheel radius
        self.L = 0.072     # distance from center to wheel

        # Correct wheel angles from URDF (radians)
        self.theta_left  = -math.pi / 6    # -30°
        self.theta_right =  math.pi / 6    # +30°
        self.theta_back  =  math.pi / 2    # +90°

        # ================= ROS INTERFACES =================
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        self.pub = self.create_publisher(
            Float64MultiArray,
            '/forward_velocity_controller/commands',
            10
        )

    # ================= KINEMATICS =================
    def compute(self, vx, vy, omega, theta):
        return (
            -math.sin(theta) * vx +
             math.cos(theta) * vy +
             self.L * omega
        ) / self.r

    # ================= CALLBACK =================
    def cmd_callback(self, msg):
        vx = msg.linear.x
        vy = msg.linear.y
        omega = msg.angular.z

        # Compute wheel speeds
        w_left  = self.compute(vx, vy, omega, self.theta_left)
        w_right = self.compute(vx, vy, omega, self.theta_right)
        w_back  = self.compute(vx, vy, omega, self.theta_back)

        # Publish
        out = Float64MultiArray()
        out.data = [w_left, w_right, w_back]

        self.pub.publish(out)


def main():
    rclpy.init()
    node = OmniKinematics()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()