#!/usr/bin/env python3
from BinaryCodeParser import BinaryCodeParser
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from UartCom import UartCom
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *
from CodeImplementations.GraphicCodeImpl import *


# Load xmlParser
binaryParser = BinaryCodeParser('blocks.xml')

# Initialize uart communication to read encoded code
# received from Arduino blocks
# Default port /dev/ttyUSB0 @9600 Bds
uartCom = UartCom()

while 1:
    frame = uartCom.readRx()
    if frame:
        binaryCode = binaryParser.convertIntArrayToBinaryChain(frame)

        #  Generate binary code
        # binaryCode = ''
        # binaryCode += binaryParser.getBinary('h_on_start')
        # binaryCode += binaryParser.getBinary('c_forever')
        # binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 15})
        # binaryCode += binaryParser.getBinary('wait_touch', {'port': 0, 'state': 0})
        # binaryCode += binaryParser.getBinary('motors_run_direction', {'port': 1, 'direction': 1, 'value': 180})
        # binaryCode += binaryParser.getBinary('motors_start_speed', {'port': 2, 'direction': 1, 'value': 90})
        # binaryCode += binaryParser.getBinary('motors_stop', {'port': 2})
        # binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 15})
        # binaryCode += binaryParser.getBinary('set_status_light', {'color': 1})
        # binaryCode += binaryParser.getBinary('c_end')

        print("Binary code is: {}".format(hex(int(binaryCode, 2))))

        # Append h_on_start event to code read from arduino, for debug purpose
        binaryCode =    binaryParser.getBinary('h_on_start') + \
                        binaryParser.getBinary('c_forever') + \
                        binaryCode + \
                        binaryParser.getBinary('c_end')
        code = binaryParser.parse(binaryCode)

        if code:
            # Chose here which code implementation you want
            # GraphicCodeImpl PythonCodeImpl Ev3DevCodeImpl
            impl = GraphicCodeImpl()

            codeConverter = CodeConverter(impl)
            code = codeConverter.convert(code)
            codeConverter.display()


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
