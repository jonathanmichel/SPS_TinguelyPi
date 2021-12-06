#!/usr/bin/env python3
from BinaryCodeParser import BinaryCodeParser
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *
from CodeImplementations.GraphicCodeImpl import *
# from UartCom import UartCom


# Load xmlParser
binaryParser = BinaryCodeParser('blocks.xml')

# Chose here which code implementation you want
# GraphicCodeImpl PythonCodeImpl Ev3DevCodeImpl
impl = PythonCodeImpl()
codeConverter = CodeConverter(impl)

boolean = binaryParser.encodeBoolean('b_touch', {'port': '1'})
# boolean = binaryParser.encodeBoolean('b_distance', {'port': '2', 'operator': 'less', 'value': 50, 'unit': 'inches'})
binaryCode = binaryParser.encodeBlock('h_on_start')
binaryCode += binaryParser.encodeBlock('c_repeat_until', {'boolean': boolean})
binaryCode += binaryParser.encodeBlock('set_status_light', {'color': 'RED'})
binaryCode += binaryParser.encodeBlock('c_end')
binaryCode += binaryParser.encodeBlock('set_status_light', {'color': 'GREEN'})

code = binaryParser.parse(binaryCode)

if code:
    codeConverter.convert(code)
    codeConverter.display()

exit()

# Initialize uart communication to read encoded code
# received from Arduino blocks
# Default port /dev/ttyUSB0 @9600 Bds
uartCom = UartCom()

while 1:
    frame = uartCom.readRx()
    if frame:
        binaryCode = binaryParser.convertIntArrayToBinaryChain(frame)
        # binaryCode += binaryParser.encodeBlock('set_status_light', {'color': 'BLACK'})
        # binaryCode += binaryParser.encodeBlock('wait_seconds', {'seconds': 17})

        """
        # Append h_on_start event to code read from arduino, for debug purpose
        binaryCode =    binaryParser.encodeBlock('h_on_start') + \
                        binaryParser.encodeBlock('c_forever') + \
                        binaryCode + \
                        binaryParser.encodeBlock('c_end')
        """

        """
        #  Software generated binary code
        try:
            binaryCode = ''
            binaryCode += binaryParser.encodeBlock('h_on_start')
            binaryCode += binaryParser.encodeBlock('c_forever')
            # binaryCode += binaryParser.encodeBlock('repeat_until', {'boolean': boolean})
            # binaryCode += binaryParser.encodeBlock('wait_until', {'boolean': boolean})
            # binaryCode += binaryParser.encodeBlock('c_if', {'boolean': boolean})
            binaryCode += binaryParser.encodeBlock('wait_seconds', {'seconds': 15})
            binaryCode += binaryParser.encodeBlock('wait_touch', {'port': '1', 'state': 'pressed'})
            binaryCode += binaryParser.encodeBlock('motors_run_direction',
                                                    {'port': 'A', 'direction': 'clockwise',
                                                    'unit': 'seconds', 'value': 180})
            binaryCode += binaryParser.encodeBlock('motors_start_speed', 
                                                     {'port': 'A', 'direction': 'clockwise', 'speed': 90})
            binaryCode += binaryParser.encodeBlock('motors_stop', {'port': 'A'})
            binaryCode += binaryParser.encodeBlock('set_status_light', {'color': 'RED'})
            binaryCode += binaryParser.encodeBlock('c_end')
        except TypeError:
            print("/!\\ Unable to correctly create binary chain")
            exit()
        """

        code = binaryParser.parse(binaryCode)

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
