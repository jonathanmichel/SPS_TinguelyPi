class Ev3DevCodeImpl:
    def __init__(self):
        self.code = ''
        self.level = 0
        self.file_header = """
# !/usr/bin/env python3
from time import time, sleep

from PIL import Image

from ev3dev2.display import Display
from ev3dev2.led import Leds
from ev3dev2.motor import Motor
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4 

lcd = Display()

leds = Leds()

leds.all_off()

logo = Image.open('/home/robot/pics/EV3.bmp')
lcd.image.paste(logo, (0,0))
lcd.update()
"""
        self.code += self.file_header
        self.motorsPorts = ['A', 'B', 'C', 'D']
        self.sensorsPorts = ['INPUT_1', 'INPUT_2', 'INPUT_3', 'INPUT_4']

    def clearCode(self):
        self.code = self.file_header
        self.level = 0

    def addLine(self, line):
        self.code += "{}{}\n".format(("\t" * self.level), line)

    def getCode(self):
        return self.code

    def display(self):
        print(self.code)

    def execute(self):
        print("No execution for Ev3DevCodeImpl")

    def missingImplementationHandler(self, block, args):
        self.addLine("# /!\\ Missing implementation for {}".format(block))

    def c_forever(self):
        self.addLine("while True:")
        self.level += 1

    def c_repeat(self, times):
        self.addLine("for i in range({}):".format(times))
        self.level += 1

    def c_else(self):
        self.level -= 1
        self.addLine("else:")
        self.level += 1

    def c_end(self):
        self.level -= 1

    def h_on_start(self):
        self.addLine("#[h_on_start]")

    def wait_seconds(self, seconds):
        self.addLine("sleep({})".format(seconds))

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

    def motors_run_direction(self, port, direction, unit, value):
        sign = -1 if direction == 1 else 1

        if 0 <= port <= 3:
            self.addLine("motor = Motor(address='{}')".format(self.motorsPorts[port]))
            if unit == 0:       # rotations
                self.addLine("motor.on_for_rotations(speed=50,rotations={})".format(value * sign))
            elif unit == 1:     # degrees
                self.addLine("motor.on_for_degrees(speed=50,degrees={})".format(value * sign))
            elif unit == 2:     # seconds
                self.addLine("motor.on_for_seconds(speed=50,seconds={})".format(value * sign))
            else:
                print("Incorrect unit")
                exit()
        else:
            print("Incorrect port value")
            exit()

    def motors_start_speed(self, port, direction, value):
        sign = -1 if direction == 1 else 1

        if 0 <= port <= 3:
            self.addLine("motor = Motor(address='{}')".format(self.motorsPorts[port]))
            self.addLine("motor.on(speed={})".format(value * sign))
        else:
            print("Incorrect port value for motors_start_speed")
            exit()

    def motors_stop(self, port):
        if 0 <= port <= 3:
            self.addLine("motor = Motor(address='{}')".format(self.motorsPorts[port]))
            self.addLine("motor.off()")
        else:
            print("Incorrect port value for motors_stop")
            exit()

    def wait_touch(self, port, state):
        if 0 <= port <= 3:
            self.addLine("touch = TouchSensor({})".format(self.sensorsPorts[port]))
            if state == 0:
                self.addLine("touch.wait_for_pressed()")
            elif state == 1:
                self.addLine("touch.wait_for_released()")
            else:
                print("Incorrect state value for wait_touch")
                exit()
        else:
            print("Incorrect port value for wait_touch")
            exit()

