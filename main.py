#!/usr/bin/env python3
from BinaryCodeHandler import BinaryCodeParser
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *
from CodeImplementations.GraphicCodeImpl import *
from UartCom import UartCom


# Load xmlParser
binaryHandler = BinaryCodeParser('definition.xml')

# Chose here which code implementation you want
# GraphicCodeImpl PythonCodeImpl Ev3DevCodeImpl
impl = GraphicCodeImpl()
codeConverter = CodeConverter(impl)

# Initialize uart communication to read encoded code
# received from Arduino blocks
# Default port /dev/ttyUSB0 @9600 Bds
uartCom = UartCom()

while 1:
    frame = uartCom.readRx()
    if frame:
        binaryCode = binaryHandler.convertIntArrayToBinaryChain(frame)

        """
        # Append h_on_start event to code read from arduino, for debug purpose
        binaryCode =    binaryHandler.encodeBlock('h_on_start') + \
                        binaryHandler.encodeBlock('c_forever') + \
                        binaryCode + \
                        binaryHandler.encodeBlock('c_end')
        """

        """
        #  Software generated binary code
        try:
            binaryCode = ''
            boolean = binaryHandler.encodeBoolean('b_touch', {'port': '1'})
            boolean = binaryHandler.encodeBoolean('b_distance', 
                                                {'port': '2', 'operator': 'less', 'value': 50, 'unit': 'inches'})
            binaryCode += binaryHandler.encodeBlock('c_repeat_until', {'boolean': boolean})
            binaryCode += binaryHandler.encodeBlock('h_on_start')
            binaryCode += binaryHandler.encodeBlock('c_forever')
            # binaryCode += binaryHandler.encodeBlock('wait_until', {'boolean': boolean})
            # binaryCode += binaryHandler.encodeBlock('c_if', {'boolean': boolean})
            binaryCode += binaryHandler.encodeBlock('wait_seconds', {'seconds': 15})
            binaryCode += binaryHandler.encodeBlock('wait_touch', {'port': '1', 'state': 'pressed'})
            binaryCode += binaryHandler.encodeBlock('motors_run_direction',
                                                    {'port': 'A', 'direction': 'clockwise',
                                                    'unit': 'seconds', 'value': 180})
            binaryCode += binaryHandler.encodeBlock('motors_start_speed', 
                                                     {'port': 'A', 'direction': 'clockwise', 'speed': 90})
            binaryCode += binaryHandler.encodeBlock('motors_stop', {'port': 'A'})
            binaryCode += binaryHandler.encodeBlock('set_status_light', {'color': 'RED'})
            binaryCode += binaryHandler.encodeBlock('c_end')
        except TypeError:
            print("/!\\ Unable to correctly create binary chain")
            exit()
        """

        code = binaryHandler.parse(binaryCode)

        if code:
            codeConverter.convert(code)
            codeConverter.display()
            # codeConverter.execute()

exit()

file = FileHandler('config.ini')
ssh = SshHandler('config.ini')

file.write(code)
ssh.sendFile()

exit()

ssh.executeCode()

try:
    while True:
        pass
except KeyboardInterrupt:
    ssh.stopCode()
    ssh.close()
