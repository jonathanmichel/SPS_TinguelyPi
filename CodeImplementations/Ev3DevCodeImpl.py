class Ev3DevCodeImpl:
    def __init__(self):
        self.code = ''
        self.level = 0
        file_header = """
# !/usr/bin/env python3
from time import time, sleep
from ev3dev2.display import Display
from ev3dev2.led import Leds
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
        self.addLine("# [h_on_start]")

    def wait_seconds(self, seconds):
        self.addLine("sleep({})".format(seconds))

    def set_status_light(self, color):
        # Scratch colors : 0: off, 1: green, 2: red, 3: orange, 4: green pulse, 5: red pulse, 6: orange pulse
        # Ev3Python2 colros : 'RED', 'GREEN', 'YELLOW', 'ORANGE, 'AMBER', 'BLACK'
        colors = ['BLACK', 'GREEN', 'RED', 'ORANGE', 'GREEN', 'RED', 'ORANGE']
        colorInt = int(color)

        # Both pairs of LEDs change their colo
        self.addLine("leds.set_color('LEFT', '" + colors[colorInt] + "')")
        self.addLine("leds.set_color('RIGHT', '" + colors[colorInt] + "')")
