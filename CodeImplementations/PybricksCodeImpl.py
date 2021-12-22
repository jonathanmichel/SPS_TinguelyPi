from CodeImplementations.CodeImpl import CodeImpl

"""
Pybricks documentation
https://pybricks.com/ev3-micropython/
"""

class PybricksCodeImpl(CodeImpl):
    def __init__(self):
        super().__init__()
        self.file_header = """#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor, ColorSensor
from pybricks.parameters import *
from pybricks.tools import *

# Initialize the EV3 Brick.
ev3 = EV3Brick()

"""
        self.code += self.file_header

    def clearCode(self):
        self.code = self.file_header
        self.level = 0

    def addLine(self, line):
        self.code += "{}{}\n".format(("\t" * self.level), line)

    def debugLine(self, function, args):
        self.addLine('# === ' + function + '(' + args + ')' + ' ===')

    ###############################
    # CodeImpl functions
    ###############################

    def execute(self):
        print("No execution for PyBricksCodeImpl")

    def missingImplementationHandler(self, block, args):
        self.addLine("# /!\\ Missing implementation for {}".format(block))

    ###############################
    # C BLOCKS IMPLEMENTATIONS
    ###############################

    def c_end(self):
        if self.level > 0:
            self.level -= 1
        else:
            print("Unexpected c_end")
            exit()

    def c_forever(self):
        self.addLine("while True:")
        self.level += 1

    def c_if(self, boolean):
        super().boolean(self, boolean)
        self.addLine("if booleanCheck:")
        self.level += 1

    def c_repeat(self, times):
        self.addLine("for i in range({}):".format(times))
        self.level += 1

    def c_repeat_until(self, boolean):
        super().boolean(self, boolean)
        self.addLine("while booleanCheck:")
        self.level += 1
        super().boolean(self, boolean)

    def c_else(self):
        self.level -= 1
        self.addLine("else:")
        self.level += 1

    ###############################
    # H BLOCKS IMPLEMENTATIONS
    ###############################

    def h_on_start(self):
        self.addLine("# [h_on_start]")

    ###############################
    # STACK BLOCKS IMPLEMENTATIONS
    ###############################

    def motors_run_direction(self, port, direction, unit, value):
        # @todo Handle speed and then as a global variable that can be changed for each motor (deg/s)
        """
        # @todo Convert speed
        Large motor maximum speed: 170 rpm = 1020 deg/s
        Medium motor maximum speed: 250 rpm = 1500 deg/s
        rpm to deg/s * 6
        """
        speed = 1000
        if self.checkMotorsPorts(port):
            sign = -1 if direction == 'counterclockwise' else 1

            self.addLine("motor = Motor(port=Port.{})".format(port))
            if unit == 'rotations':
                self.addLine("motor.run_angle(speed={}, rotation_angle={}, then=Stop.HOLD, wait=True)"
                             .format(speed, 360 * value * sign))
            elif unit == 'degrees':
                self.addLine("motor.run_angle(speed={}, rotation_angle={}, then=Stop.HOLD, wait=True)"
                             .format(speed, value * sign))
            elif unit == 'seconds':
                self.addLine("motor.run_time(speed={}, time={}, then=Stop.HOLD, wait=True)"
                             .format(speed * sign, value * 1000))   # value is in s and as to be passed in ms
            else:
                print("Incorrect unit")
                exit()
        else:
            print("Incorrect port value")
            exit()

    def motors_start_speed(self, port, direction, speed):
        sign = -1 if direction == 'counterclockwise' else 1
        # Convert speed (see motors_run_direction)
        if 0 <= speed <= 100:
            speed = speed * 10
        else:
            speed = 1000
        if self.checkMotorsPorts(port):
            self.addLine("motor = Motor(port=Port.{})".format(port))
            self.addLine("motor.run(speed={})".format(sign * speed))
        else:
            print("Incorrect port value for motors_start_speed")
            exit()

    def motors_stop(self, port):
        if self.checkMotorsPorts(port):
            self.addLine("motor = Motor(port=Port.{})".format(port))
            self.addLine("motor.stop()")
        else:
            print("Incorrect port value for motors_stop")
            exit()

    def set_status_light(self, color):
        # Scratch colors enum : BLACK, GREEN, RED, ORANGE, GREEN_PULSE, RED_PULSE, ORANGE_PULSE
        # Pybricks supported colors : BLACK, BLUE, GREEN, YELLOW, RED, WHITE, BROWN, ORANGE, PURPLE
        supported_colors = ['BLACK', 'GREEN', 'RED', 'ORANGE']

        # Not supported : 'GREEN_PULSE', 'RED_PULSE', 'ORANGE_PULSE'

        if color in supported_colors:
            # Both pairs of LEDs change their color
            self.addLine("ev3.light.on(Color.{})".format(color))
            # self.addLine("leds.set_color('RIGHT', '" + color + "')")
        else:
            self.addLine("# Unsupported color {}".format(color))
            self.addLine("ev3.light.off()")

    def wait_seconds(self, seconds):
        # seconds is in s and has to be passed in ms
        self.addLine("wait({})".format(seconds * 1000))

    def wait_until(self, boolean):
        self.addLine("# /// wait_until \\\\\\")
        self.addLine("booleanCheck = False")
        self.addLine("while not booleanCheck:")
        self.level += 1
        super().boolean(self, boolean)
        self.level -= 1
        self.addLine("# \\\\\\ wait_until /// ")

    def wait_touch(self, port, state):
        if self.checkSensorsPorts(port):
            self.addLine("touch = TouchSensor(Port.S{})".format(port))
            if state == 'pressed':
                self.addLine("while not touch.pressed():")
                self.addLine("\t pass")
            elif state == 'released':
                self.addLine("while touch.pressed():")
                self.addLine("\t pass")
            else:
                print("Incorrect state value for wait_touch")
                exit()
        else:
            print("Incorrect port value for wait_touch")
            exit()

    ###############################
    # BOOLEAN IMPLEMENTATIONS
    ###############################

    def b_touch(self, port):
        if self.checkSensorsPorts(port):
            self.addLine("touch = TouchSensor(Port.S{})".format(port))
            self.addLine("booleanCheck = touch.pressed()")

    def b_distance(self, port, operator, value, unit):
        if self.checkSensorsPorts(port):
            op = self.convertOperator(operator)
            if op:
                self.addLine("ultrasonic = UltrasonicSensor(Port.S{})".format(port))
                # @todo Current version does not use unit
                # value is in cm and has to be passed in mm
                self.addLine("booleanCheck = True if ultra.distance() {} {} else False"
                             .format(op, value * 10))

    ###############################
    # CUSTOM IMPLEMENTATIONS
    ###############################

    def set_trap_door(self, state):
        port = 'A'
        if state == 'open':
            self.motors_run_direction(port=port, direction="clockwise", unit="degrees", value=-360)
        elif state == 'close':
            self.motors_run_direction(port=port, direction="clockwise", unit="degrees", value=360)
        else:
            print("Incorrect state value")
            exit()

    def start_crawler(self, direction):
        port = 'B'

        # self.motors_start_speed(port=port, direction="clockwise", 500)
        self.motors_run_direction(port=port, direction=direction, unit="seconds", value=3)
