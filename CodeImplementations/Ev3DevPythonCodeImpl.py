from CodeImplementations.CodeImpl import CodeImpl


class Ev3DevPythonCodeImpl(CodeImpl):
    def __init__(self):
        super().__init__()
        self.file_header = """
# !/usr/bin/env python3
from time import time, sleep

from ev3dev2.led import Leds
from ev3dev2.motor import Motor
from ev3dev2.sensor.lego import TouchSensor, UltrasonicSensor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4 

leds = Leds()

leds.all_off()
"""
        self.code += self.file_header

    def clearCode(self):
        self.code = self.file_header
        self.level = 0

    def addLine(self, line):
        self.code += "{}{}\n".format(("\t" * self.level), line)

    def debugLine(self, function, args):
        self.addLine('# === ' + function + '(' + args + ')' + '===')

    ###############################
    # CodeImpl functions
    ###############################

    def execute(self):
        print("No execution for Ev3DevCodeImpl")

    def missingImplementationHandler(self, block, args):
        self.addLine("# /!\\ Missing implementation for {}".format(block))

    ###############################
    # C BLOCKS IMPLEMENTATIONS
    ###############################

    def c_end(self):
        self.level -= 1

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
        sign = -1 if direction == 'counterclockwise' else 1
        speed = 50

        if self.checkMotorsPorts(port):
            self.addLine("motor = Motor(address='{}')".format(port))
            if unit == 'rotations':
                self.addLine("motor.on_for_rotations(speed={},rotations={})".format(speed * sign, value))
            elif unit == 'degrees':
                self.addLine("motor.on_for_degrees(speed={},degrees={})".format(speed * sign, value))
            elif unit == 'seconds':
                self.addLine("motor.on_for_seconds(speed={},seconds={})".format(speed * sign, value))
            else:
                print("Incorrect unit")
                exit()
        else:
            print("Incorrect port value")
            exit()

    def motors_start_speed(self, port, direction, speed):
        sign = -1 if direction == 'counterclockwise' else 1

        if self.checkMotorsPorts(port):
            self.addLine("motor = Motor(address='{}')".format(port))
            self.addLine("motor.on(speed={})".format(speed * sign))
        else:
            print("Incorrect port value for motors_start_speed")
            exit()

    def motors_stop(self, port):
        if self.checkMotorsPorts(port):
            self.addLine("motor = Motor(address='{}')".format(port))
            self.addLine("motor.off()")
        else:
            print("Incorrect port value for motors_stop")
            exit()

    def set_status_light(self, color):
        # Scratch colors enum : BLACK, GREEN, RED, ORANGE, GREEN_PULSE, RED_PULSE, ORANGE_PULSE
        # Ev3Python2 supported colors : BLACK, GREEN, RED, ORANGE, YELLOW, AMBER
        supported_colors = ['BLACK', 'GREEN', 'RED', 'ORANGE']

        # Not supported : 'GREEN_PULSE', 'RED_PULSE', 'ORANGE_PULSE'

        if color in supported_colors:
            # Both pairs of LEDs change their color
            self.addLine("leds.set_color('LEFT', '" + color + "')")
            self.addLine("leds.set_color('RIGHT', '" + color + "')")
        else:
            self.addLine("# Unsupported color {}".format(color))
            self.addLine("leds.animate_stop()")
            self.addLine("leds.all_off()")

    def wait_seconds(self, seconds):
        self.addLine("sleep({})".format(seconds))

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
            self.addLine("touch = TouchSensor({})".format(port))
            if state == 'pressed':
                self.addLine("touch.wait_for_pressed()")
            elif state == 'released':
                self.addLine("touch.wait_for_released()")
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
            self.addLine("# <b_touch {}>".format(port))
            self.addLine("touch = TouchSensor({})".format(port))
            self.addLine("booleanCheck = touch.is_pressed")

    def b_distance(self, port, operator, value, unit):
        if self.checkSensorsPorts(port):
            self.addLine("# b_distance {} {} {} {}".format(port, operator, value, unit))
            self.addLine("booleanCheck = False")  # @todo Implement

    ###############################
    # CUSTOM IMPLEMENTATIONS
    ###############################

    def set_trap_door(self, state):
        speed = 50
        address = 'A'
        if state == 'open':
            self.addLine("motor = Motor(address='{}')".format(address))
            self.addLine("motor.on_for_degrees(speed={},degrees=360)".format(speed))
        elif state == 'close':
            self.addLine("motor = Motor(address='{}')".format(address))
            self.addLine("motor.on_for_degrees(speed={},degrees=-360)".format(speed))
        else:
            print("Incorrect state value")
            exit()

    def start_crawler(self, direction):
        sign = -1 if direction == 'counterclockwise' else 1
        speed = 20
        address = 'B'

        self.addLine("motor = Motor(address='{}')".format(address))
        self.addLine("motor.on(speed={})".format(speed * sign))

        self.wait_seconds(5)
        self.motors_stop('B')
