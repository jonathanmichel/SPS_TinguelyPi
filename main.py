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
impl = GraphicCodeImpl()
codeConverter = CodeConverter(impl)


# b_distance: id = 0x41, argument = 0b1001111100001000 = 0x9F08, size = 24 with id
#       => Frame: 0x[size]419F08 = 00011000010000011001111100001000
# b_touch: id = 0x43, argument = 0b11000000 = 0xC0, size = 16 with id
#   => Frame: 0x[size]43C0 = 000100000100001111000000
binaryCode = binaryParser.encodeFunction('h_on_start')
binaryCode += binaryParser.encodeFunction('c_if', {'boolean': '000100000100001111000000'})
binaryCode += binaryParser.encodeFunction('set_status_light', {'color': 'RED'})
binaryCode += binaryParser.encodeFunction('c_else')
binaryCode += binaryParser.encodeFunction('motors_stop', {'port': 'A'})
binaryCode += binaryParser.encodeFunction('c_end')


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
        #binaryCode += binaryParser.encodeFunction('set_status_light', {'color': 'BLACK'})
        #binaryCode += binaryParser.encodeFunction('wait_seconds', {'seconds': 17})

        """
        # Append h_on_start event to code read from arduino, for debug purpose
        binaryCode =    binaryParser.encodeFunction('h_on_start') + \
                        binaryParser.encodeFunction('c_forever') + \
                        binaryCode + \
                        binaryParser.encodeFunction('c_end')
        """

        """
        #  Software generated binary code
        try:
            binaryCode = ''
            binaryCode += binaryParser.encodeFunction('h_on_start')
            binaryCode += binaryParser.encodeFunction('c_forever')
            binaryCode += binaryParser.encodeFunction('wait_seconds', {'seconds': 15})
            binaryCode += binaryParser.encodeFunction('wait_touch', {'port': '1', 'state': 'pressed'})
            binaryCode += binaryParser.encodeFunction('motors_run_direction',
                                                    {'port': 'A', 'direction': 'clockwise',
                                                    'unit': 'seconds', 'value': 180})
            binaryCode += binaryParser.encodeFunction('motors_start_speed', 
                                                     {'port': 'A', 'direction': 'clockwise', 'speed': 90})
            binaryCode += binaryParser.encodeFunction('motors_stop', {'port': 'A'})
            binaryCode += binaryParser.encodeFunction('set_status_light', {'color': 'RED'})
            binaryCode += binaryParser.encodeFunction('c_end')
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
