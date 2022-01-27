#!/usr/bin/env python3
from datetime import datetime
import os

from FrameEncoder import FrameEncoder
from FrameDecoder import FrameDecoder
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from CodeImplementations.Ev3DevPythonCodeImpl import *
from CodeImplementations.PythonCodeImpl import *
from CodeImplementations.GraphicCodeImpl import *
from CodeImplementations.PybricksCodeImpl import *
from UartCom import UartCom
from Gpio import Gpio

# Load decoder with xml definition
decoder = FrameDecoder('definitionAscii.xml')
# Load encoder with xml definition
encoder = FrameEncoder('definitionAscii.xml')

# Chose here which code implementation you want
# GraphicCodeImpl PythonCodeImpl Ev3DevPythonCodeImpl PybricksCodeImpl
graphicCodeImpl = GraphicCodeImpl()
codeConverterGraphic = CodeConverter(graphicCodeImpl)

# Initialize uart communication to read encoded code
# received from Arduino blocks
# Default port /dev/ttyUSB0 @9600 Bds
uartCom = UartCom()
gpio = Gpio()

# Crate handler for file writting and
# ssh communication with the EV3
file = FileHandler('config.ini')
ssh = SshHandler('config.ini')


# Remotely stop code and close ssh session
def endAll():
    ssh.stopCode()
    ssh.close()
    exit()


print("Waiting for code ...")

try:
    while True:
        # Read full frame received from UART
        frame = uartCom.readRx()
        if frame:
            os.system('clear')
            lastUpdate = datetime.now()
            print("Received frame at {}: {}".format(lastUpdate.strftime("%H:%M:%S"), frame))

            # Append h_on_start at the beginning of the frame read from Arduino
            frame = encoder.encodeBlock('h_on_start') + '|' + frame

            """
            #  Software generated binary code (debug)            
            frame.appendBlock('h_on_start')
            frame.appendBlock('wait_seconds', {'seconds': 15})
            frame.appendBlock('c_forever')
            boolean = frame.encodeBoolean('b_touch', {'port': '1'})
            frame.appendBlock('c_if', {'boolean': boolean})
            frame.appendBlock('set_status_light', {'color': 'GREEN'})
            frame.appendBlock('motors_start_speed', {'port': 'B', 'direction': 'clockwise', 'speed': 50})
            frame.appendBlock('wait_touch', {'port': '1', 'state': 'released'})
            frame.appendBlock('c_else')
            frame.appendBlock('motors_stop', {'port': 'B'})
            frame.appendBlock('set_status_light', {'color': 'RED'})
            frame.appendBlock('wait_touch', {'port': '1', 'state': 'pressed'})
            frame.appendBlock('c_end')
            
            frame.print()
            """

            # Generate code array from binary chain
            code_array = decoder.parseFrame(frame)

            if code_array:
                # Convert code array in a graphical representation for debug purposes
                converted_code = codeConverterGraphic.convert(code_array)
                if converted_code:
                    # Display graphical representation
                    codeConverterGraphic.display()

                    # Check if user wants to "upload" the current code to the EV3
                    # @todo Replace by asynchron call
                    if gpio.isKeyPressed():
                        print(10 * "PROGRAM ")

                        codeConverterPybricks = CodeConverter(PybricksCodeImpl())
                        if codeConverterPybricks.convert(code_array):
                            codeConverterPybricks.display()
                            
                            # file.write(codeConverterPybricks.getCode())
                            # ssh.sendFile()

                            # ssh.executeCode()
                        else:
                            print("Error when converting code for Pybricks")

                        print("Press button to continue")
                        gpio.waitClicked()

                        print(10 * "RESTART ")

                    continue
                else:
                    codeConverterGraphic.display()
                    print("/!\\ Error when converting code - Function implementations missing")

            else:
                print("/!\\ Unable to parse binary")

except KeyboardInterrupt:
    # Catch keyboard interrupt and close program
    endAll()
