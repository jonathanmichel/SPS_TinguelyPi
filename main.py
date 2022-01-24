#!/usr/bin/env python3
from BinaryCodeHandler import BinaryCodeParser
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from CodeImplementations.Ev3DevPythonCodeImpl import *
from CodeImplementations.PythonCodeImpl import *
from CodeImplementations.GraphicCodeImpl import *
from CodeImplementations.PybricksCodeImpl import *
from UartCom import UartCom
from Gpio import Gpio


# Load xmlParser
binaryHandler = BinaryCodeParser('definition.xml')

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
            # Convert frame array to str binary chain
            binaryCode = binaryHandler.convertIntArrayToBinaryChain(frame)

            # Append h_on_start at the beginning of the code read from Arduino
            binaryCode = binaryHandler.encodeBlock('h_on_start') + binaryCode

            """
            #  Software generated binary code (debug)
            try:
                binaryCode = ''
                binaryCode += binaryHandler.encodeBlock('h_on_start')
                boolean = binaryHandler.encodeBoolean('b_touch', {'port': '1'})
                binaryCode += binaryHandler.encodeBlock('c_forever')
                binaryCode += binaryHandler.encodeBlock('c_if', {'boolean': boolean})
                binaryCode += binaryHandler.encodeBlock('set_status_light', {'color': 'GREEN'})
                binaryCode += binaryHandler.encodeBlock('motors_start_speed',
                                                        {'port': 'B', 'direction': 'clockwise', 'speed': 50})
                binaryCode += binaryHandler.encodeBlock('wait_touch', {'port': '1', 'state': 'released'})
                binaryCode += binaryHandler.encodeBlock('c_else')
                binaryCode += binaryHandler.encodeBlock('motors_stop', {'port': 'B'})
                binaryCode += binaryHandler.encodeBlock('set_status_light', {'color': 'RED'})
                binaryCode += binaryHandler.encodeBlock('wait_touch', {'port': '1', 'state': 'pressed'})
                binaryCode += binaryHandler.encodeBlock('c_end')
                binaryCode += binaryHandler.encodeBlock('c_end')
            except TypeError:
                print("/!\\ Unable to correctly create binary chain")
                exit()
            """

            # Generate code array from binary chain
            code_array = binaryHandler.parse(binaryCode)

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
