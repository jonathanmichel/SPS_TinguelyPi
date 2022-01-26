"""
Author: Jonathan Michel
Date:   22.12.2021
This class reads the UART port to receive a frame from the Arduino of the upper block
The frame has to follow a specific protocol. For additional information, see the
documentation.
"""

import serial


class UartCom:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.readingFrame = False
        self.rxBuffer = []

        print("Initialise serial communication on port {} at {} bauds".format(port, baudrate))

        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        print("\t Serial communication initialised")

        self.START_SYMBOL = '#'
        self.END_SYMBOL = '!'

    def readRx(self):
        data = self.serial.read(1)
        # We check that a new byte has been read
        if len(data) > 0:
            if data == self.START_SYMBOL:
                # We start frame reception
                self.readingFrame = True
                self.rxBuffer = []  # Clear rx buffer
            elif self.readingFrame:  # If we already received the start symbol
                # We check if we received the end symbol (!)
                if data == self.END_SYMBOL:
                    return self.rxBuffer
                # otherwise we check that we didn't miss the stop symbol (frame too big)
                elif len(self.rxBuffer) > 255:
                    # ... if so, we wait for a new frame
                    self.readingFrame = False
                    self.rxBuffer = []           # Clear rx buffer
                else:    # if not, we simply store data
                    self.rxBuffer.append(data)
            else:
                pass    # We wait for the start symbol

        return None
