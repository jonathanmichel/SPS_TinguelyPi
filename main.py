#!/usr/bin/env python3
import time
import sys
import signal

from BinaryCodeParser import BinaryCodeParser
from CodeConverter import CodeConverter
from SshHandler import SshHandler
from FileHandler import FileHandler
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *


# Load xmlParser
binaryParser = BinaryCodeParser('blocks.xml')

# Generate binary code
binaryCode = ''
binaryCode += binaryParser.getBinary('h_on_start')
binaryCode += binaryParser.getBinary('motors_run_direction', {'port': 1, 'direction': 1, 'unit': 1, 'value': 180})
#binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 1})
binaryCode += binaryParser.getBinary('motors_run_direction', {'port': 0, 'direction': 0, 'unit': 0, 'value': 1})
binaryCode += binaryParser.getBinary('motors_run_direction', {'port': 2, 'direction': 0, 'unit': 0, 'value': 3})
#binaryCode += binaryParser.getBinary('c_forever')
#binaryCode += binaryParser.getBinary('set_status_light', {'color': 1})
#binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 1})
#binaryCode += binaryParser.getBinary('c_end')

print("Binary code is: {}\n".format(binaryCode))

code = binaryParser.parse(binaryCode)

# pythonImpl = PythonCodeImpl()
pythonImpl = Ev3DevCodeImpl()
codeConverter = CodeConverter(pythonImpl)
code = codeConverter.convert(code)
codeConverter.display()

# exit()

file = FileHandler('config.ini')
ssh = SshHandler('config.ini')

file.write(code)
ssh.sendFile()

# exit()

ssh.executeCode()

try:
    while True:
        pass
except KeyboardInterrupt:
    ssh.stopCode()
    ssh.close()
