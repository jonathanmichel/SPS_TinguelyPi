
# !/usr/bin/env python3
from ev3dev2.led import Leds
from time import time, sleep

leds = Leds()

leds.all_off()
        # [h_on_start]
while True:
	leds.set_color('LEFT', 'ORANGE')
	leds.set_color('RIGHT', 'ORANGE')
	sleep(2)
	leds.set_color('LEFT', 'GREEN')
	leds.set_color('RIGHT', 'GREEN')
	sleep(1)
