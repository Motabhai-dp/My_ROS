#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


MSG = """
Reading from the keyboard
---------------------------
   u    i    o
   j    k    l
   m    ,    .

Shift = holonomic
q/z = speed up/down
CTRL-C to quit
"""

MOVE_BINDINGS = {
    'i': (0.5774, 0.0, -0.5774),
    'o': (0.3, -1.0, -1.0),
    'j': (0.3333, -0.3333, 0.3333),
    'l': (-0.3333, 0.3333, -0.3333),
    'u': (1.0, 1.0, 0.0),
    ',': (-0.5774, 0.0, 0.5774),
    '.': (0.0, 1.0, -1.0),
    'm': (1.0, -1.0, 0.0),
    'O': (-1.0, 1.0, 0.0),
    'I': (-1.0, 0.0, 1.0),
    'J': (1.0, 2.0, 1.0),
    'L': (-1.0, -2.0, -1.0),
    'U': (0.0, -1.0, 1.0),
    '<': (1.0, 0.0, -1.0),
    '>': (0.0, 1.0, -1.0),
    'M': (1.0, -1.0, 0.0),
}

SPEED_BINDINGS = {
    'q': 1.1,
    'z': 0.9,
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

        self.pub_left = self.create_publisher(
            Float64, '/omni_bot/left_wheel_controller/command', 10)
        self.pub_front = self.create_publisher(
            Float64, '/omni_bot/front_wheel_controller/command', 10)
        self.pub_right = self.create_publisher(
            Float64, '/omni_bot/right_wheel_controller/command', 10)

        self.speed = 1.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.settings = termios.tcgetattr(sys.stdin)

        print(MSG)

        self.timer = self.create_timer(0.1, self.loop)

    def loop(self):
        key = get_key(self.settings)

        if key in MOVE_BINDINGS:
            self.x, self.y, self.z = MOVE_BINDINGS[key]

        elif key in SPEED_BINDINGS:
            self.speed *= SPEED_BINDINGS[key]

        elif key == '\x03':
            self.stop_robot()
            rclpy.shutdown()
            return

        else:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0

        self.publish()

    def publish(self):
        msg_l = Float64()
        msg_f = Float64()
        msg_r = Float64()

        msg_l.data = self.x * self.speed
        msg_f.data = self.y * self.speed
        msg_r.data = self.z * self.speed

        self.pub_left.publish(msg_l)
        self.pub_front.publish(msg_f)
        self.pub_right.publish(msg_r)

    def stop_robot(self):
        msg = Float64()
        msg.data = 0.0
        self.pub_left.publish(msg)
        self.pub_front.publish(msg)
        self.pub_right.publish(msg)


def main():
    rclpy.init()
    node = OmniTeleop()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()