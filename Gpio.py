import RPi.GPIO as GPIO
import time

class Gpio:

    def __init__(self):
        self.LAUNCH_GPIO = 8

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.LAUNCH_GPIO, GPIO.IN)

    def isKeyPressed(self):
        if GPIO.input(self.LAUNCH_GPIO):
            return True
        return False

    def waitReleased(self):
        while GPIO.input(self.LAUNCH_GPIO) == GPIO.HIGH:
            pass

    def waitClicked(self):
        self.waitReleased()

        time.sleep(0.02)    # avoid bounces

        while GPIO.input(self.LAUNCH_GPIO) == GPIO.LOW:
            pass

        time.sleep(0.02) # avoid bounces

        self.waitReleased()
