#!/usr/bin/env python3

import sys
import select
import termios
import tty
import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


# Body motion commands (vx, vy, omega)
MOVE_BINDINGS = {
    'i': (1.0, 0.0, 0.0),    # forward
    'k': (-1.0, 0.0, 0.0),   # reverse
    'j': (0.0, 1.0, 0.0),    # left
    'l': (0.0, -1.0, 0.0),   # right
    '<': (0.0, 0.0, 1.0),    # rotate left
    '>': (0.0, 0.0, -1.0),   # rotate right
}


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1) if rlist else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class OmniTeleop(Node):

    def __init__(self):
        super().__init__('omni_teleop')

        self.pub = self.create_publisher(
            Float64MultiArray,
            '/forward_velocity_controller/commands',
            10
        )

        # robot parameters
        self.r = 0.016
        self.L = 0.072

        # wheel angles (adjust only if needed)
        self.theta = [
            math.radians(150),  # left
            math.radians(30),   # right
            math.radians(270)   # back
        ]

        self.speed = 10.0

        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0

        self.settings = termios.tcgetattr(sys.stdin)
        self.create_timer(0.1, self.loop)

    def compute_wheels(self, vx, vy, omega):
        wheels = []

        # PURE ROTATION (no translation)
        if omega != 0.0:
            return [(self.L * omega) / self.r] * 3

        # PURE TRANSLATION using matrix
        for t in self.theta:
            w = (-math.sin(t) * vx +
                 math.cos(t) * vy) / self.r
            wheels.append(w)

        # ENFORCE ZERO ROTATION (remove bias)
        avg = sum(wheels) / 3.0
        wheels = [w - avg for w in wheels]

        return wheels

    def loop(self):
        key = get_key(self.settings)

        if key in MOVE_BINDINGS:
            self.vx, self.vy, self.omega = MOVE_BINDINGS[key]
        elif key == '\x03':
            self.stop_robot()
            rclpy.shutdown()
            return
        else:
            self.vx = 0.0
            self.vy = 0.0
            self.omega = 0.0

        self.publish()

    def publish(self):
        w = self.compute_wheels(self.vx, self.vy, self.omega)

        msg = Float64MultiArray()
        msg.data = [
            w[0] * self.speed,
            w[1] * self.speed,
            w[2] * self.speed
        ]

        self.pub.publish(msg)

    def stop_robot(self):
        msg = Float64MultiArray()
        msg.data = [0.0, 0.0, 0.0]
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = OmniTeleop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()