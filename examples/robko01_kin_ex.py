#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""

MIT License

Copyright (c) [2023] [Orlin Dimitrov]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial SerialPortions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import time
from machine import Pin
from pyaccelstepper.accel_stepper import AccelStepper, InterfaceType, MultiStepper

#region File Attributes

__author__ = "Orlin Dimitrov"
"""Author of the file."""

__copyright__ = "Copyright 2023, Orlin Dimitrov"
"""Copyright holder"""

__credits__ = []
"""Credits"""

__license__ = "MIT"
"""License: https:# choosealicense.com/licenses/mit/"""

__version__ = "1.0.0"
"""Version of the file."""

__maintainer__ = "Orlin Dimitrov"
"""Name of the maintainer."""

__email__ = "robko01@8bitclub.com"
"""E-mail of the author."""

__status__ = "Debug"
"""File status."""

#endregion

#region Variables

__time_to_stop = False
"""Time to stop flag.
"""

__pins = {
    "Enable": Pin(2, Pin.OUT),
    "M1_DIR": Pin(4, Pin.OUT),
    "M1_STP": Pin(0, Pin.OUT),
    "M2_DIR": Pin(17, Pin.OUT),
    "M2_STP": Pin(16, Pin.OUT),
    "M3_DIR": Pin(25, Pin.OUT),
    "M3_STP": Pin(26, Pin.OUT),
    "M4_DIR": Pin(12, Pin.OUT),
    "M4_STP": Pin(13, Pin.OUT),
    "M5_DIR": Pin(27, Pin.OUT),
    "M5_STP": Pin(14, Pin.OUT),
    "M6_DIR": Pin(32, Pin.OUT),
    "M6_STP": Pin(33, Pin.OUT),
    "M1_LIMIT": Pin(36, Pin.IN, Pin.PULL_UP),
    "M2_LIMIT": Pin(39, Pin.IN, Pin.PULL_UP),
    "M3_LIMIT": Pin(34, Pin.IN, Pin.PULL_UP),
    "M6_LIMIT": Pin(35, Pin.IN, Pin.PULL_UP),
    }
"""IO pins.
"""

#endregion

class Robot():

    S1 = -59800 / 90
    S2 = 59200 / 90
    S3 = -36100 / 90.7
    S5 = 500
    S5A2 = -(55000 / 90) * 0.04
    S5A3 = (55000 / 90) * 0.7

    Q1_ZERO = 75.32
    Q2_ZERO = -23.24
    Q3_ZERO = 37.35

    A5_ZERO = 20

    A5_UNGRIP_DIST = 6

    ACCELERATION = 1E+10
    MOTOR_SPEED = 1000 * 3
    MOTOR_SLOW_SPEED = MOTOR_SPEED / 2
    MOTOR_MAX_SPEED = MOTOR_SPEED
    MOTOR_SPEED_5 = MOTOR_SPEED * 0.6
    MOTOR_SLOW_SPEED_5 = MOTOR_SPEED_5 / 2
    MOTOR_MAX_SPEED_5 = MOTOR_SPEED_5

    def __init__(self, **kwarg):

        self.__positions = [0,0,0,0]

        self.__a5_offset_a2_a3_ = 0
        self.__oldA2 = 0
        self.__oldA3 = 0

        self.__base = None
        self.__shoulder = None
        self.__elbow = None
        self.__gripper = None

        self.__kinematics_controller = None
        """Main controller.
        """

        self.__pr_controller = None
        """Differential controler.
        """

        self.__pins = {}
        if "pins" in kwarg:
            self.__pins = kwarg["pins"]

        self.__axis = {
            "base": {
                "DIR": self.__pins["M1_DIR"],
                "STP": self.__pins["M1_STP"]
                },
            "shoulder": {
                "DIR": self.__pins["M2_DIR"],
                "STP": self.__pins["M2_STP"]
                },
            "elbow": {
                "DIR": self.__pins["M3_DIR"],
                "STP": self.__pins["M3_STP"]
                },
            "ld": {
                "DIR": self.__pins["M4_DIR"],
                "STP": self.__pins["M4_STP"]
                },
            "rd": {
                "DIR": self.__pins["M5_DIR"],
                "STP": self.__pins["M5_STP"]
                },
            "gripper": {
                "DIR": self.__pins["M6_DIR"],
                "STP": self.__pins["M6_STP"]
                },
            }

        self.__init_pins()
        self.__init_motors()

            # Enable drivers.
        self.__pins["Enable"].value(0)

    def __pulse(self, axis, direction=0, pulse=2):
        # Set directio.
        self.__axis[axis]["DIR"].value(direction)
        # Generate pulse.
        self.__axis[axis]["STP"].value(1)
        time.sleep_us(pulse)
        self.__axis[axis]["STP"].value(0)
        time.sleep_us(pulse)
        self.__axis[axis]["STP"].value(1)

    def __init_pins(self):

        # Disable drivers.
        __pins["Enable"].value(1)

        # Init the pin state.
        __pins["M1_DIR"].value(1)
        __pins["M1_STP"].value(1)
        __pins["M2_DIR"].value(1)
        __pins["M2_STP"].value(1)
        __pins["M3_DIR"].value(1)
        __pins["M3_STP"].value(1)
        __pins["M4_DIR"].value(1)
        __pins["M4_STP"].value(1)
        __pins["M5_DIR"].value(1)
        __pins["M5_STP"].value(1)
        __pins["M6_DIR"].value(1)
        __pins["M6_STP"].value(1)

    def __init_motors(self):

        self.__base = AccelStepper(
            cb_cw=[lambda: self.__pulse("base", 1)],
            cb_ccw=[lambda: self.__pulse("base", 0)],
            interface=InterfaceType.FUNCTION,
            enable=True
            )
        self.__base.speed_scale = 1
        self.__base.max_speed = 1000.0
        self.__base.acceleration = 1000.0
        self.__base.speed = 1.0

        self.__shoulder = AccelStepper(
            cb_cw=[lambda: self.__pulse("shoulder", 1)],
            cb_ccw=[lambda: self.__pulse("shoulder", 0)],
            interface=InterfaceType.FUNCTION,
            enable=True
            )
        self.__shoulder.speed_scale = 1
        self.__shoulder.max_speed = 500.0
        self.__shoulder.acceleration = 500.0
        self.__shoulder.speed = 1.0

        self.__elbow = AccelStepper(
            cb_cw=[lambda: self.__pulse("elbow", 1)],
            cb_ccw=[lambda: self.__pulse("elbow", 0)],
            interface=InterfaceType.FUNCTION,
            enable=True
            )
        self.__elbow.speed_scale = 1
        self.__elbow.max_speed = 500.0
        self.__elbow.acceleration = 500.0
        self.__elbow.speed = 1.0

        self.__gripper = AccelStepper(
            cb_cw=[lambda: self.__pulse("gripper", 1)],
            cb_ccw=[lambda: self.__pulse("gripper", 0)],
            interface=InterfaceType.FUNCTION,
            enable=True
            )
        self.__gripper.speed_scale = 1
        self.__gripper.max_speed = 500.0
        self.__gripper.acceleration = 500.0
        self.__gripper.speed = 1.0

        self.__kinematics_controller = MultiStepper()
        self.__kinematics_controller.add(self.__elbow)
        self.__kinematics_controller.add(self.__shoulder)
        self.__kinematics_controller.add(self.__base)
        self.__kinematics_controller.add(self.__gripper)

        self.__ld = AccelStepper(
            cb_cw=[lambda: self.__pulse("ld", 1)],
            cb_ccw=[lambda: self.__pulse("ld", 0)],
            interface=InterfaceType.FUNCTION,
            enable=True
            )
        self.__ld.speed_scale = 1
        self.__ld.max_speed = 1500.0
        self.__ld.acceleration = 1000.0
        self.__ld.speed = 1.0

        self.__rd = AccelStepper(
            cb_cw=[lambda: self.__pulse("rd", 1)],
            cb_ccw=[lambda: self.__pulse("rd", 0)],
            interface=InterfaceType.FUNCTION,
            enable=True
            )
        self.__rd.speed_scale = 1
        self.__rd.max_speed = 1500.0
        self.__rd.acceleration = 1000.0
        self.__rd.speed = 1.0

        self.__pr_controller = MultiStepper()
        self.__pr_controller.add(self.__ld)
        self.__pr_controller.add(self.__rd)

    def send_task_to_steppers(self, a1, a2, a3, a5):

        a5 = a5 * Robot.S5

        self.__a5_offset_a2_a3_ = self.__a5_offset_a2_a3_ + Robot.S5A2 * (a2 - self.__oldA2) + Robot.S5A3 * (a3 - self.__oldA3)
        a5 = a5 + self.__a5_offset_a2_a3_
        self.__oldA2 = a2
        self.__oldA3 = a3

        self.__positions[0] = round(a1 * Robot.S1)
        self.__positions[1] = round(a2 * Robot.S2)
        self.__positions[2] = round(a3 * Robot.S3)
        self.__positions[3] = round(a5)

        # Enable drivers.
        __pins["Enable"].value(0)

        # Set position.
        self.__kinematics_controller.move_to(self.__positions)

        # Achieve the position.
        self.__kinematics_controller.run_speed_to_position()

        # Reset position controllers for nex round.
        self.__base.set_current_position(0)
        self.__shoulder.set_current_position(0)
        self.__elbow.set_current_position(0)
        self.__gripper.set_current_position(0)

        # Disable drivers.
        __pins["Enable"].value(1)

        print(self.__positions)

def main():
    """Main function
    """

    robot = Robot(pins=__pins)
    robot.send_task_to_steppers(0.35, 0.120, 0.120, 0.35)
    print("DONE")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
       __time_to_stop = True
