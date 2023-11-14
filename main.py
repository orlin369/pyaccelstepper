#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""

Stepper Motor Controller

Copyright (C) [2020] [Orlin Dimitrov]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import signal
import time

from accel_stepper.accel_stepper import AccelStepper
from accel_stepper.interface_type import InterfaceType

#region Variables

# Define some steppers and the pins the will use
__motor_controller = None

__time_to_stop = False
"""Time to stop flag."""

#endregion

def cw():
    global __motor_controller

    print("CW: {}: {}".format(__motor_controller.current_position, time.time()))

def ccw():
    global __motor_controller

    print("CCW: {}: {}".format(__motor_controller.current_position, time.time()))

def interupt_handler(signum, frame):
    """Interupt handler."""

    global __time_to_stop, __motor_controller

    __time_to_stop = True
    __motor_controller.stop()


def main():
    """Main function"""    

    global __time_to_stop, __motor_controller

    # Add signal handler.
    signal.signal(signal.SIGINT, interupt_handler)
    signal.signal(signal.SIGTERM, interupt_handler)

    # interface=InterfaceType.FULL4WIRE
    # interface=InterfaceType.HALF4WIRE
    interface=InterfaceType.FULL3WIRE
    # interface=InterfaceType.HALF3WIRE
    # interface=InterfaceType.FULL2WIRE
    # interface=InterfaceType.DRIVER
    # interface=InterfaceType.FUNCTION

    __motor_controller = AccelStepper(
        cb_cw=[cw],
        cb_ccw=[ccw],
        interface=interface,\
        # pins=[0,1,2,3],\
        # pins_inverted=[False, False, False, False],\
        enable=True\
        )

    __motor_controller.speed_scale = 1
    __motor_controller.max_speed = 55.0
    __motor_controller.acceleration = 5.0
    __motor_controller.set_speed = 1.0
    __motor_controller.move_to(100.0)

    while not __time_to_stop:
        # Change direction at the limits
        if __motor_controller.distance_to_go == 0:
            __motor_controller.move_to(-__motor_controller.current_position)
        __motor_controller.run()

if __name__ == "__main__":
    main()