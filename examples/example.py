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

import signal
import time

from pyaccelstepper.accel_stepper import AccelStepper, InterfaceType

#region File Attributes

__author__ = "Orlin Dimitrov"
"""Author of the file."""

__copyright__ = "Copyright 2023, Orlin Dimitrov"
"""Copyright holder"""

__credits__ = []
"""Credits"""

__license__ = "MIT"
"""License: https://choosealicense.com/licenses/mit/"""

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

# Define some steppers and the pins the will use
__motor_controller = None

__time_to_stop = False
"""Time to stop flag."""

#endregion

def cw():
    global __motor_controller

    print(f"CW\t{__motor_controller.current_position}\t{time.time()}")

def ccw():
    global __motor_controller

    print(f"CCW\t{__motor_controller.current_position}\t{time.time()}")

def interrupt_handler(signum, frame):
    """Interrupt handler."""

    global __time_to_stop, __motor_controller

    __time_to_stop = True
    __motor_controller.stop()

def main():
    """Main function"""    

    global __time_to_stop, __motor_controller

    # Add signal handler.
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)

    # interface=InterfaceType.FULL4WIRE
    # interface=InterfaceType.HALF4WIRE
    # interface=InterfaceType.FULL3WIRE
    # interface=InterfaceType.HALF3WIRE
    # interface=InterfaceType.FULL2WIRE
    # interface=InterfaceType.DRIVER
    interface=InterfaceType.FUNCTION

    __motor_controller = AccelStepper(
        cb_cw=[cw],
        cb_ccw=[ccw],
        interface=interface,
        pins=[4,5,6,7],
        pins_inverted=[False, False, False, False],
        enable=True
        )

    __motor_controller.speed_scale = 1
    __motor_controller.max_speed = 100.0
    __motor_controller.acceleration = 5.0
    __motor_controller.speed = 1.0
    __motor_controller.move_to(100.0)

    while not __time_to_stop:
        # Change direction at the limits
        if __motor_controller.distance_to_go == 0:
            __motor_controller.move_to(-__motor_controller.current_position)
        __motor_controller.run()

if __name__ == "__main__":
    main()
