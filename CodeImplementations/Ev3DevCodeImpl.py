class Ev3DevCodeImpl:
    def __init__(self):
        self.code = ''
        self.level = 0
        file_header = """
# !/usr/bin/env python3
from time import time, sleep
from ev3dev2.display import Display
from ev3dev2.led import Leds
from ev3dev2.motor import Motor
from PIL import Image

lcd = Display()

leds = Leds()

leds.all_off()

logo = Image.open('/home/robot/pics/EV3.bmp')
lcd.image.paste(logo, (0,0))
lcd.update()
        """
        self.code += file_header

    def addLine(self, line):
        self.code += "{}{}\n".format(("\t" * self.level), line)

    def getCode(self):
        return self.code

    def display(self):
        print("=" * 15)
        print("Converter code for Ev3Dev")
        print("=" * 15)
        print(self.code)
        print("=" * 15)

    def execute(self):
        print("No execution for Ev3DevCodeImpl")

    def clear(self):
        self.code = ''

    def c_forever(self):
        self.addLine("while True:")
        self.level += 1

    def c_end(self):
        self.level -= 1

    def h_on_start(self):
        self.addLine("#[h_on_start]")

    def wait_seconds(self, seconds):
        self.addLine("sleep({})".format(seconds))

    def set_status_light(self, color):
        # Scratch colors : 0: off, 1: green, 2: red, 3: orange, 4: green pulse, 5: red pulse, 6: orange pulse
        # Ev3Python2 colros : 'RED', 'GREEN', 'YELLOW', 'ORANGE, 'AMBER', 'BLACK'
        colors = ['BLACK', 'GREEN', 'RED', 'ORANGE', 'GREEN_PULSE', 'RED_PULSE', 'ORANGE_PULSE']
        color_int = int(color)

        if 1 <= color_int <= 3:
            # Both pairs of LEDs change their color
            self.addLine("leds.set_color('LEFT', '" + colors[color_int] + "')")
            self.addLine("leds.set_color('RIGHT', '" + colors[color_int] + "')")
        elif 4 <= color_int <= 6:
            print('Pulse not supported for now')
            exit()
        else:
            self.addLine("leds.animate_stop()")
            self.addLine("leds.all_off()")

    def motors_run_direction(self, port, direction, unit, value):
        ports = ['A', 'B', 'C', 'D']
        sign = -1 if direction == 1 else 1

        if 0 <= port <= 3:
            self.addLine("motor = Motor(address='{}')".format(ports[port]))
            if unit == 0:   # rotations
                self.addLine("motor.on_for_rotations(speed=50,rotations={})".format(value * sign))
            elif unit == 1: # degrees
                self.addLine("motor.on_for_degrees(speed=50,degrees={})".format(value * sign))
            elif unit == 2: # seconds
                self.addLine("motor.on_for_seconds(speed=50,seconds={})".format(value * sign))
            else:
                print("Incorrect unit")
                exit()
        else:
            print("Incorrect port value")
            exit()
