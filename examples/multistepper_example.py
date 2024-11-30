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

__motors = None
"""Motors controller
"""

__time_to_stop = False
"""Time to stop flag.
"""

__pins = {
    "Enable": Pin(2, Pin.OUT),
    "M1_DIR": Pin(4, Pin.OUT),
    "M1_STP": Pin(0, Pin.OUT),
    "M2_DIR": Pin(17, Pin.OUT),
    "M2_STP": Pin(16, Pin.OUT),
    "M3_DIR": Pin(12, Pin.OUT),
    "M3_STP": Pin(13, Pin.OUT),
    "M4_DIR": Pin(25, Pin.OUT),
    "M4_STP": Pin(26, Pin.OUT),
    "M5_DIR": Pin(27, Pin.OUT),
    "M5_STP": Pin(14, Pin.OUT),
    "M6_DIR": Pin(32, Pin.OUT),
    "M6_STP": Pin(33, Pin.OUT),
    "M1_LIMIT": Pin(36, Pin.IN, Pin.PULL_UP),
    "M2_LIMIT": Pin(39, Pin.IN, Pin.PULL_UP),
    "M3_LIMIT": Pin(34, Pin.IN, Pin.PULL_UP),
    "M6_LIMIT": Pin(35, Pin.IN, Pin.PULL_UP),
    }

__axis = {
    "base": {
        "DIR": __pins["M1_DIR"],
        "STP": __pins["M1_STP"]
        },
    "shoulder": {
        "DIR": __pins["M2_DIR"],
        "STP": __pins["M2_STP"]
        },
    "elbow": {
        "DIR": __pins["M3_DIR"],
        "STP": __pins["M3_STP"]
        },
    "ld": {
        "DIR": __pins["M4_DIR"],
        "STP": __pins["M4_STP"]
        },
    "rd": {
        "DIR": __pins["M5_DIR"],
        "STP": __pins["M5_STP"]
        },
    "gripper": {
        "DIR": __pins["M6_DIR"],
        "STP": __pins["M6_STP"]
        },
    }

#endregion

def pulse(axis, direction=0, pulse=2):
    global __axis
    
    # Set directio.
    __axis[axis]["DIR"].value(direction)

    # Generate pulse.
    __axis[axis]["STP"].value(1)
    time.sleep_us(pulse)
    __axis[axis]["STP"].value(0)
    time.sleep_us(pulse)
    __axis[axis]["STP"].value(1)

def init():
    global __pins, __motors

    # Disable drivers.
    __pins["Enable"].value(1)
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

    m_base = AccelStepper(
        cb_cw=[lambda: pulse("base", 1)],
        cb_ccw=[lambda: pulse("base", 0)],
        interface=InterfaceType.FUNCTION,
        enable=True
        )
    m_base.speed_scale = 1
    m_base.max_speed = 1000.0
    m_base.acceleration = 1000.0
    m_base.speed = 1.0

    m_shoulder = AccelStepper(
        cb_cw=[lambda: pulse("shoulder", 1)],
        cb_ccw=[lambda: pulse("shoulder", 0)],
        interface=InterfaceType.FUNCTION,
        enable=True
        )
    m_shoulder.speed_scale = 1
    m_shoulder.max_speed = 500.0
    m_shoulder.acceleration = 500.0
    m_shoulder.speed = 1.0

    __motors = MultiStepper()
    __motors.add(m_base)
    __motors.add(m_shoulder)

def main():
    """Main function"""    

    global __pins, __time_to_stop, __motors

    init()

    # Enable drivers.
    __pins["Enable"].value(0)

    __motors.move_to([300, 150])
    __motors.run_speed_to_position()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
       __time_to_stop = True
