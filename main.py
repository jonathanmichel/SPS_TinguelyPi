#!/usr/bin/env python3
from BinaryCodeParser import BinaryCodeParser
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *
from CodeImplementations.GraphicCodeImpl import *
from UartCom import UartCom


# Load xmlParser
binaryParser = BinaryCodeParser('blocks.xml')

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
        binaryCode = binaryParser.convertIntArrayToBinaryChain(frame)

        # """
        # Append h_on_start event to code read from arduino, for debug purpose
        binaryCode =    binaryParser.getBinary('h_on_start') + \
                        binaryParser.getBinary('c_forever') + \
                        binaryCode + \
                        binaryParser.getBinary('c_end')
        # """

        #  Software generated binary code
        """
        try:
            binaryCode = ''
            binaryCode += binaryParser.getBinary('h_on_start')
            binaryCode += binaryParser.getBinary('c_forever')
            binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 15})
            binaryCode += binaryParser.getBinary('wait_touch', {'port': '1', 'state': 'pressed'})
            binaryCode += binaryParser.getBinary('motors_run_direction',
                                                 {'port': 'A', 'direction': 'clockwise', 'unit': 'seconds', 'value': 180})
            binaryCode += binaryParser.getBinary('motors_start_speed', {'port': 'A', 'direction': 'clockwise', 'value': 90})
            binaryCode += binaryParser.getBinary('motors_stop', {'port': 'A'})
            binaryCode += binaryParser.getBinary('set_status_light', {'color': 'RED'})
            binaryCode += binaryParser.getBinary('c_end')
        except TypeError:
            print("/!\\ Unable to correctly create binary chain")
            exit()
        """
        
        code = binaryParser.parse(binaryCode)

        if code:
            code = codeConverter.convert(code)
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
