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

file = FileHandler('config.ini')
ssh = SshHandler('config.ini')


def endAll():
    ssh.stopCode()
    ssh.close()
    exit()

try:
    while True:
        frame = uartCom.readRx()
        if frame:
            binaryCode = binaryHandler.convertIntArrayToBinaryChain(frame)

            # Append h_on_start event to code read from arduino, for debug purpose
            binaryCode = binaryHandler.encodeBlock('h_on_start') + \
                         binaryCode
                         # binaryHandler.encodeBlock('c_end')
                         # binaryHandler.encodeBlock('c_forever') + \

            """
            #  Software generated binary code
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

            code_array = binaryHandler.parse(binaryCode)

            if code_array:
                converted_code = codeConverterGraphic.convert(code_array)
                if converted_code:
                    codeConverterGraphic.display()

                    if gpio.isKeyPressed():
                        print(10 * "PROGRAM ")

                        codeConverterPybricks = CodeConverter(PybricksCodeImpl())
                        if codeConverterPybricks.convert(code_array):
                            file.write(codeConverterPybricks.getCode())
                            ssh.sendFile()

                            ssh.executeCode()
                        else:
                            print("Error when converting code for Pybricks")

                        print("Press button to continue")
                        gpio.waitClicked()

                        print(10 * "RESTART ")

                        ssh.stopCode()

                    continue

                else:
                    codeConverterGraphic.display()
                    print("/!\\ Error when converting code - Function implementations missing")

            else:
                print("/!\\ Unable to parse binary")

except KeyboardInterrupt:
    endAll()
