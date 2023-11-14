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

import time
import math

from accel_stepper.direction import Direction
from accel_stepper.interface_type import InterfaceType

from accel_stepper.controllers.pin_mode import PinMode
from accel_stepper.controllers.pin_state import PinState
from accel_stepper.controllers.dummy.dummy import Dummy

from accel_stepper.utils.utils import Utils

class AccelStepper:
    """Stepper Motor Controller"""

#region Variables

    __interface = InterfaceType.FUNCTION
    """Signals interface.
    """

    __forward = []
    """Forward list of callbacks.
    """

    __backward = []
    """Backward list of callbacks.
    """

    __enable_pin = 255
    """Enable pin index.
    """

    __pins = [0, 1, 2, 3]
    """Pins that signals will go to.
    """

    __pins_inverted = [False, False, False, False]
    """Inverted pins mask.
    """

    __enable_inverted = False
    """Enable pin inverted mask.
    """

    __controller = Dummy()
    """Controller that will pass the signals to the pins.
    """

    __speed = 0
    """Speed
    """

    __max_speed = 0
    """Maximum speed.
    """

    __acceleration = 0
    """Acceleration
    """

    __current_pos = 0
    """Axis current position.
    """

    __target_pos = 0
    """Axis target position.
    """

    __step_interval = 0
    """Time between steps.
    """

    __min_pulse_width = 1
    """Minimum pulse width.
    """

    __last_step_time = 0
    """LAst step time.
    """
    __direction = Direction.CCW
    """Direction flag.
    """

    __n = int(0)
    """State machine index.
    """    

    __sqrt_twoa = 1.0

    __c0 = 0.0
  
    __cn = 0.0

    __cmin = 1.0

    __scale = 1.0 # 1000000.0 # 3.0

#endregion

#region Constructor

    def __init__(self, **config):
        """[summary]
        """

        if "interface" in config and config["interface"] is not None:
            self.__interface = config["interface"]

        if "controller" in config and config["controller"] is not None:
            self.__controller = config["controller"]

        if "cb_cw" in config and config["cb_cw"] is not None:
            self.__forward = config["cb_cw"]

        if "cb_ccw" in config and config["cb_ccw"] is not None:
            self.__backward = config["cb_ccw"]

        if "pins" in config and config["pins"] is not None:
            self.__pins = config["pins"]

        # Pins inverted.
        if "pins_inverted" in config and config["pins_inverted"] is not None:
            self.__pins_inverted = config["pins_inverted"]

        # Enable outputs.
        enable = False
        if "enable" in config and config["enable"] is not None:
            enable = config["enable"]

        # Enable pin inverted.
        if "enable_inverted" in config and config["enable_inverted"] is not None:
            self.__enable_inverted = config["enable_inverted"]

        for index in range(3):
            self.__pins_inverted[index] = 0

        # Some reasonable default
        self.set_acceleration = 1
        self.speed = 0.0
        self.max_speed = 1.0
        self.enable_outputs(enable)

#endregion

#region Properties

    @property
    def direction(self):
        """Axis direction.

        Returns:
            enum: Axis direction.
        """

        return self.__direction

    @property
    def distance_to_go(self):
        """Distance to go.

        Returns:
            int: Distance to go in steps.
        """

        return self.target_position - self.current_position

    @property
    def target_position(self):
        """TArget position.

        Returns:
            int: Target position in steps.
        """

        return self.__target_pos

    @property
    def current_position(self):
        """Current position of the axis.

        Returns:
            int: Current position in steps.
        """

        return self.__current_pos

    @property
    def speed(self):
        """Returns the speed.

        Returns:
            float: Speed.
        """

        return self.__speed

    @speed.setter
    def speed(self, speed):
        """Set the speed.

        Args:
            speed (float): Speed of the axis.
        """

        if speed == self.__speed:
            return

        speed = Utils.constrain(speed, -self.__max_speed, self.__max_speed)

        if speed == 0.0:
            self.__step_interval = 0
        else:
            self.__step_interval = abs(self.__scale / speed)

            if speed > 0.0:
                self.__direction = Direction.CW
            else:
                self.__direction = Direction.CCW

        self.__speed = speed

    @property
    def max_speed(self):
        """Returns maximum speed.

        Returns:
            float: Maximum speed.
        """

        return self.__max_speed

    @max_speed.setter
    def max_speed(self, speed):
        """Set maximum speed.

        Args:
            speed (float): Float speed.
        """

        if speed < 0.0:
            speed = -speed

        if self.__max_speed != speed:
            self.__max_speed = speed
            self.__cmin = self.__scale / speed

        # Recompute self.__n from current speed and adjust speed if accelerating or cruising
        if self.__n > 0:
            self.__n = ((self.__speed * self.__speed) / (2.0 * self.__acceleration)) # Equation 16
            self.__compute_new_speed()

    @property
    def speed_scale(self):
        """Returns the speed.

        Returns:
            float: Speed.
        """

        return self.__scale

    @speed_scale.setter
    def speed_scale(self, scale):
        """Set the speed.

        Args:
            speed (float): Speed of the axis.
        """

        self.__scale = scale

    @property
    def acceleration(self):
        """Returns acceleration.

        Returns:
            float: Acceleration.
        """

        return self.__acceleration

    @acceleration.setter
    def acceleration(self, acceleration):
        """Set acceleration.

        Args:
            acceleration (float): Acceleration
        """

        if acceleration == 0.0:
            return

        if acceleration < 0.0:
            acceleration = -acceleration

        if self.__acceleration != acceleration:
            # Recompute self.__n per Equation 17
            self.__n = self.__n * (self.__acceleration / acceleration)
            # New c0 per Equation 7, with correction per Equation 15
            self.__c0 = 0.676 * math.sqrt(2.0 / acceleration) * self.__scale # Equation 15
            self.__acceleration = acceleration
            self.__compute_new_speed()

    @property
    def min_pulse_width(self):
        """Return minimum pulse width.
        """

        return self.__min_pulse_width

    @min_pulse_width.setter
    def min_pulse_width(self, value):
        """Set minimum pulse width.

        Args:
            value (float): Pulse width.
        """

        self.__min_pulse_width = value

    @property
    def enable_pin(self):
        """Return enable pin.
        """

        return self.__enable_pin

    @enable_pin.setter
    def senable_pin(self, value):
        """Set enable pin.

        Args:
            value (int): Enable pin index.
        """

        self.__enable_pin = value


#endregion

#region Private Methods

    def __step_0(self):
        """0 pin step function (ie for functional usage)"""

        if self.__speed > 0:
            if self.__forward is not None:
                for item in self.__forward:
                    if item is not None:
                        item()
        else:
            if self.__backward is not None:
                for item in self.__backward:
                    if item is not None:
                        item()

    def __step_1(self):
        """1 pin step function (ie for stepper drivers)
            This is passed the current step number (0 to 7)
            Subclasses can override"""

        # self.__pins[0] is step, self.__pins[1] is direction
        if self.__direction == Direction.CCW:
            self.__set_output_pins(0b10) # Set direction first else get rogue pulses
            self.__set_output_pins(0b11) # step HIGH

        elif self.__direction == Direction.CW:
            self.__set_output_pins(0b00) # Set direction first else get rogue pulses
            self.__set_output_pins(0b00) # step HIGH

        # Caution 200ns setup time
        # Delay the minimum allowed pulse width
        time.sleep(self.__min_pulse_width)

        if self.__direction == Direction.CCW:
            self.__set_output_pins(0b00) # step LOW

        elif self.__direction == Direction.CW:
            self.__set_output_pins(0b10) # step LOW

    def __step_2(self, step):
        """2 pin step function
            This is passed the current step number (0 to 7)
            Subclasses can override"""

        step = step & 0x3

        if step == 0: # 01
            self.__set_output_pins(0b10)

        elif step == 1: # 11
            self.__set_output_pins(0b11)

        elif step == 2: # 10
            self.__set_output_pins(0b01)

        elif step == 3: # 00
            self.__set_output_pins(0b00)

    def __step_3(self, step):
        """3 pin step function
            This is passed the current step number (0 to 7)
            Subclasses can override"""

        step = step % 3

        if step == 0:    # 100
            self.__set_output_pins(0b100)

        elif step == 1:    # 001
            self.__set_output_pins(0b001)

        elif step == 2:    #010
            self.__set_output_pins(0b010)

    def __step_4(self, step):
        """4 pin step function for half stepper
            This is passed the current step number (0 to 7)
            Subclasses can override"""

        step = step % 3

        if step == 0:    # 1010
            self.__set_output_pins(0b0101)

        elif step == 1:    # 0110
            self.__set_output_pins(0b0110)

        elif step == 2:    #0101
            self.__set_output_pins(0b1010)

        elif step == 3:    #1001
            self.__set_output_pins(0b1001)

    def __step_6(self, step):
        """3 pin half step function
            This is passed the current step number (0 to 7)
            Subclasses can override"""

        step = step % 6

        if step == 0:    # 100
            self.__set_output_pins(0b100)

        elif step == 1:    # 101
            self.__set_output_pins(0b101)

        elif step == 2:    # 001
            self.__set_output_pins(0b001)

        elif step == 3:    # 011
            self.__set_output_pins(0b011)

        elif step == 4:    # 010
            self.__set_output_pins(0b010)

        elif step == 5:    # 011
            self.__set_output_pins(0b110)

    def __step_8(self, step):
        """4 pin half step function
        This is passed the current step number (0 to 7)
        Subclasses can override"""

        step = step & 7

        if step == 0:    # 1000
            self.__set_output_pins(0b0001)

        elif step == 1:    # 1010
            self.__set_output_pins(0b0101)

        elif step == 2:    # 0010
            self.__set_output_pins(0b0100)

        elif step == 3:    # 0110
            self.__set_output_pins(0b0110)

        elif step == 4:    # 0100
            self.__set_output_pins(0b0010)

        elif step == 5:    #0101
            self.__set_output_pins(0b1010)

        elif step == 6:    # 0001
            self.__set_output_pins(0b1000)

        elif step == 7:    #1001
            self.__set_output_pins(0b1001)

    def __step(self, step):
        """Subclasses can override."""

        if self.__interface is InterfaceType.FUNCTION:
            self.__step_0()

        elif self.__interface is InterfaceType.DRIVER:
            self.__step_1()

        elif self.__interface is InterfaceType.FULL2WIRE:
            self.__step_2(step)

        elif self.__interface is InterfaceType.FULL3WIRE:
            self.__step_3(step)

        elif self.__interface is InterfaceType.FULL4WIRE:
            self.__step_4(step)

        elif self.__interface is InterfaceType.HALF3WIRE:
            self.__step_6(step)

        elif self.__interface is InterfaceType.HALF4WIRE:
            self.__step_8(step)

    def __compute_new_speed(self):
        """Compute new speed.
        """

        distance_to = self.distance_to_go # +ve is clockwise from current location

        steps_to_stop = ((self.speed * self.speed) / (2.0 * self.acceleration)) # Equation 16

        if (distance_to == 0) and (steps_to_stop <= 1):
            # We are at the target and its time to stop
            self.__step_interval = 0
            self.__speed = 0.0
            self.__n = 0
            return

        if distance_to > 0:
            # We are anticlockwise from the target
            # Need to go clockwise from here, maybe decelerate now

            if self.__n > 0:
                # Currently accelerating, need to deceleration now? Or maybe going the wrong way?
                if (steps_to_stop >= distance_to) or (self.__direction == Direction.CCW):
                    self.__n = -steps_to_stop # Start deceleration

            elif self.__n < 0:
                # Currently decelerating, need to accel again?
                if (steps_to_stop < distance_to) and (self.__direction == Direction.CW):
                    self.__n = -self.__n # Start acceleration

        elif distance_to < 0:
            # We are clockwise from the target
            # Need to go anticlockwise from here, maybe decelerate

            if self.__n > 0:
                # Currently accelerating, need to deceleration now? Or maybe going the wrong way?
                if (steps_to_stop >= -distance_to) or (self.__direction == Direction.CW):
                    self.__n = -steps_to_stop # Start deceleration

            elif self.__n < 0:
                # Currently decelerating, need to accel again?
                if (steps_to_stop < -distance_to) and (self.__direction == Direction.CCW):
                    self.__n = -self.__n # Start acceleration

        # Need to accelerate or decelerate
        if self.__n == 0:

            # First step from stopped
            self.__cn = self.__c0

            if distance_to > 0:
                self.__direction = Direction.CW
            else:
                self.__direction = Direction.CCW

        else:
            # Subsequent step. Works for accel (n is +_ve) and decel (n is -ve).
            self.__cn = self.__cn - ((2.0 * self.__cn) / ((4.0 * self.__n) + 1)) # Equation 13
            self.__cn = max(self.__cn, self.__cmin)

        self.__n += 1
        self.__n = int(self.__n)

        self.__step_interval = self.__cn
        self.__speed = self.__scale / self.__cn
        if self.__direction == Direction.CCW:
            self.__speed = -self.__speed

    def __set_output_pins(self, mask):
        """You might want to override this to implement eg serial output
            bit 0 of the mask corresponds to self.__pins[0]
            bit 1 of the mask corresponds to self.__pins[1]
        """

        num_pins = 2

        if (self.__interface is InterfaceType.FULL4WIRE) or \
            (self.__interface is InterfaceType.HALF4WIRE):

            num_pins = 4

        elif (self.__interface is InterfaceType.FULL3WIRE) or \
            (self.__interface is InterfaceType.HALF3WIRE):

            num_pins = 3

        for index in range(num_pins):
            state = 0

            if mask & (1 << index):
                state = not self.__pins_inverted[index] == 0
            else:
                state = self.__pins_inverted[index] == 0

            self.__controller.digital_write(self.__pins[index], state)

#endregion

#region Public Methods

    def enable_outputs(self, state):
        """Enable outputs.
        """

        if not self.__interface:
            return

        # Enable
        if state:
            self.__controller.pin_mode(self.__pins[0], PinMode.Output)
            self.__controller.pin_mode(self.__pins[1], PinMode.Output)

            if (self.__interface == InterfaceType.FULL4WIRE) or \
                (self.__interface == InterfaceType.HALF4WIRE):
                self.__controller.pin_mode(self.__pins[2], PinMode.Output)
                self.__controller.pin_mode(self.__pins[3], PinMode.Output)

            elif (self.__interface == InterfaceType.FULL3WIRE) or \
                (self.__interface == InterfaceType.HALF3WIRE):
                self.__controller.pin_mode(self.__pins[2], PinMode.Output)

            if self.__enable_pin != 255:
                self.__controller.pin_mode(self.__enable_pin, PinMode.Output)
                self.__controller.digital_write(\
                    self.__enable_pin,\
                    PinState.High ^ self.__enable_inverted)

        # Disable
        else:
            if not self.__interface:
                return

            self.__set_output_pins(0) # Handles inversion automatically

            if self.__enable_pin != 255:
                self.__controller.pin_mode(self.__enable_pin, PinMode.Output)
                self.__controller.digital_write(\
                    self.__enable_pin,\
                    PinState.Low ^ self.__enable_inverted)

    def set_current_position(self, position):
        """Useful during initializations or after initial positioning Sets speed to 0
        """

        self.__target_pos = position
        self.__current_pos = position
        self.__n = 0
        self.__step_interval = 0
        self.speed = 0.0

    def move_to(self, absolute):
        """Move the axis to position.

        Args:
            absolute (int): Absolute position in steps.
        """

        if self.__target_pos != absolute:
            self.__target_pos = absolute

        self.__compute_new_speed()
        # compute new n?

    def move(self, relative):
        """Move the axis with relative steps.

        Args:
            relative (int): Relative position in steps.
        """

        self.move_to(self.__current_pos + relative)

    def run_speed(self):
        """Implements steps according to the current step interval
            You must call this at least once per step
            returns True if a step occurred
        """

        # Don't do anything unless we actually have a step interval
        if self.__step_interval <= 0.0:
            return False

        time_now = time.time()

        if (time_now - self.__last_step_time) >= self.__step_interval:
            if self.__direction == Direction.CW:
                # Clockwise
                self.__current_pos += 1
            else:
                # Anticlockwise
                self.__current_pos -= 1

            self.__step(self.__current_pos)

            self.__last_step_time = time_now # Caution: does not account for costs in __step()

            return True

        return False

    def run(self):
        """Run the motor to implement speed and acceleration
        in order to proceed to the target position
            You must call this at least once per step, preferably in your main loop
            If the motor is in the desired position, the cost is very small
            returns True if the motor is still running to the target position.
        """

        if self.run_speed():
            self.__compute_new_speed()

        return (self.speed != 0.0) or (self.distance_to_go != 0)

    def run_to_position(self):
        """Blocks until the target position is reached and stopped"""

        while self.run():
            pass

    def run_speed_to_position(self):
        """Run speed to position.

        Returns:
            int: When finish.
        """

        if self.__target_pos == self.__current_pos:
            return False

        if self.__target_pos > self.__current_pos:
            self.__direction = Direction.CW
        else:
            self.__direction = Direction.CCW

        return self.run_speed()

    def run_to_new_positions(self, position):
        """Blocks until the new target position is reached."""

        self.move_to(position)
        self.run_to_position()

    def is_running(self):
        """Is running.

        Returns:
            bool: Is running flag.
        """

        return not (self.__speed == 0.0) and (self.__target_pos == self.__current_pos)

    def stop(self):
        """Stop
        """

        if self.__speed != 0.0:
             # Equation 16 (+integer rounding)
            steps_to_stop = ((self.__speed * self.__speed) / (2.0 * self.__acceleration)) + 1

        if self.__speed > 0:
            self.move(steps_to_stop)

        else:
            self.move(-steps_to_stop)

#endregion
