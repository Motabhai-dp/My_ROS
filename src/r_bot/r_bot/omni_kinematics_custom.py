#!/usr/bin/env python3

import math
import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float64MultiArray


class OmniKeyboardControl(Node):

    def __init__(self):
        super().__init__('omni_keyboard_control')

        # ================= ROBOT PARAMETERS =================
        self.r = 0.03
        self.L = 0.072

        # ================= WHEEL ANGLES =================
        # Derived from URDF
        self.theta_left  =  0      # -30°
        self.theta_right =  math.pi / 3     # +30°
        self.theta_back  =  math.pi / 1     # +90°

        # ================= MOTION STATES =================
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0

        # Speeds
        self.linear_speed = 0.5
        self.angular_speed = 1.0

        # ================= ROS PUBLISHER =================
        self.pub = self.create_publisher(
            Float64MultiArray,
            '/forward_velocity_controller/commands',
            10
        )

        # Timer loop
        self.timer = self.create_timer(
            0.05,
            self.control_loop
        )

        self.get_logger().info("""

================ HOLONOMIC CONTROL ================

w : -X MOTION
s : +X MOTION

a : +Y MOTION
d : -Y MOTION

z : ROTATE CCW
x : ROTATE CW

k : STOP
q : QUIT

===================================================

""")

    # ================= KINEMATICS =================
    def compute(self, vx, vy, omega, theta):

        return (
            -math.sin(theta) * vx +
             math.cos(theta) * vy +
             self.L * omega
        ) / self.r

    # ================= KEYBOARD =================
    def get_key(self):

        tty.setraw(sys.stdin.fileno())

        rlist, _, _ = select.select(
            [sys.stdin],
            [],
            [],
            0.01
        )

        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            self.settings
        )

        return key

    # ================= CONTROL LOOP =================
    def control_loop(self):

        key = self.get_key()

        # Reset every cycle
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0

        # ==================================================
        # KEY MAPPING
        # ==================================================

        # -X / +X MOTION
        if key == 'w':
            self.vx = -self.linear_speed

        elif key == 's':
            self.vx = self.linear_speed

        # +Y / -Y MOTION
        elif key == 'a':
            self.vy = self.linear_speed

        elif key == 'd':
            self.vy = -self.linear_speed

        # ROTATION
        elif key == 'z':
            self.omega = self.angular_speed

        elif key == 'x':
            self.omega = -self.angular_speed

        # STOP
        elif key == 'k':
            self.vx = 0.0
            self.vy = 0.0
            self.omega = 0.0

        # QUIT
        elif key == 'q':
            self.destroy_node()
            rclpy.shutdown()
            return

        # ================= WHEEL SPEEDS =================

        w_left = self.compute(
            self.vx,
            self.vy,
            self.omega,
            self.theta_left
        )

        w_right = self.compute(
            self.vx,
            self.vy,
            self.omega,
            self.theta_right
        )

        w_back = self.compute(
            self.vx,
            self.vy,
            self.omega,
            self.theta_back
        )

        # ================= PUBLISH =================

        msg = Float64MultiArray()

        msg.data = [
            w_left,
            w_right,
            w_back
        ]

        self.pub.publish(msg)

        # ================= DEBUG =================

        print(
            f"\r"
            f"VX={self.vx:.2f} "
            f"VY={self.vy:.2f} "
            f"W={self.omega:.2f} | "
            f"L={w_left:.2f} "
            f"R={w_right:.2f} "
            f"B={w_back:.2f}",
            end=''
        )


def main(args=None):

    rclpy.init(args=args)

    node = OmniKeyboardControl()

    node.settings = termios.tcgetattr(
        sys.stdin
    )

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            node.settings
        )

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()