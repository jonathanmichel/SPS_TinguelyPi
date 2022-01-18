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
        self.binaryCtn = 0
        self.rxBuffer = []

        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        self.START_HEAD = 0x1
        self.END_TRANSMISSION = 0x4

    def readRx(self):
        data_byte = self.serial.read(1)
        # We check that a new byte has been read
        if len(data_byte) > 0:
            data = int.from_bytes(data_byte, "big")
            # If binaryCtn is not 0, we are currently receiving data ...
            # print("rx: {} \t ({}, {})".format(data_byte, data, hex(data)))

            if self.binaryCtn > 0:
                # ... so we fill the array
                self.rxBuffer.append(data)
                # .. and decrement binaryCtn
                self.binaryCtn -= 1

                if self.binaryCtn == 0:
                    frame = ''
                    for b in self.rxBuffer:
                        frame += hex(b)[2:]

                    print("Full frame received: {}".format(frame))

                    return self.rxBuffer

                # Check if rxBuffer is too big
                # 255 is the longer frame supported in Arduino code
                if len(self.rxBuffer) > 255:
                    print("Too long frame received")
                    self.rxBuffer = []
                    self.binaryCtn = 0
                    return

            elif self.binaryCtn == -1:  # current byte is supposed to be frame length (0-255)
                self.binaryCtn = data
                # print("Start reading frame: {} byte(s) long".format(self.binaryCtn))
            elif data == self.START_HEAD:  # // If we are not receiving new data, we wait SOH
                # Once SOH is received, the next byte indicates the data length
                # By changing binaryCtn, we activate binary receiving. Next step will be to read frame length
                self.binaryCtn = -1
                self.rxBuffer = []      # Clear rx buffer

        return None
