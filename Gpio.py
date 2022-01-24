"""
Author: Jonathan Michel
Date:   22.12.2021
This class provides an interface for the "programming" button that is used to
launch the code on the EV3
It reads input 8 state (see LAUNCH_GPIO)
"""

import RPi.GPIO as GPIO
import time


class Gpio:
    def __init__(self):
        self.LAUNCH_GPIO = 8    # physical pin 8
        self.callback_function = None

        # Uses physical pin numbers on the GPIO connector
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.LAUNCH_GPIO, GPIO.IN)

    def isKeyPressed(self):
        if GPIO.input(self.LAUNCH_GPIO):
            return True
        return False

    def configureCallback(self, callback_function):
        GPIO.add_event_detect(self.LAUNCH_GPIO, GPIO.RISING, callback=callback_function)

    def waitReleased(self):
        while GPIO.input(self.LAUNCH_GPIO) == GPIO.HIGH:
            pass

    def waitClicked(self):
        self.waitReleased()

        time.sleep(0.02)    # avoid bounces

        while GPIO.input(self.LAUNCH_GPIO) == GPIO.LOW:
            pass

        time.sleep(0.02)    # avoid bounces

        self.waitReleased()
