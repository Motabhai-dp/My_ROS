import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


class OmniKinematics(Node):

    def __init__(self):
        super().__init__('omni_kinematics')

        # Robot parameters
        self.r = 0.016   # wheel radius
        self.L = 0.072   # distance from center to wheel
        omega = 0

        # Wheel angles (verified 120° layout)
        self.theta_left  = math.radians(120)
        self.theta_right = math.radians(0)
        self.theta_back  = math.radians(240)

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

    def compute(self, vx, vy, omega, theta):
        return (-math.sin(theta) * vx +
                math.cos(theta) * vy +
                self.L * omega) / self.r

    def cmd_callback(self, msg):
        # --- FRAME ALIGNMENT FIX ---
        # ensures "i" key = forward in your view
        vx = msg.linear.y
        vy = -msg.linear.x
        omega = msg.angular.z

        # Compute wheel velocities
        w_left  = self.compute(vx, vy, omega, self.theta_left)
        w_right = self.compute(vx, vy, omega, self.theta_right)
        w_back  = self.compute(vx, vy, omega, self.theta_back)

        # Publish in correct order
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