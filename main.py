#!/usr/bin/env python3
import time
import sys
import signal

from BinaryCodeParser import *
from CodeConverter import *
from SshHandler import *
from FileHandler import *
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *


# Load xmlParser
binaryParser = BinaryCodeParser('blocks.xml')

# Generate binary code
binaryCode = ''
binaryCode += binaryParser.getBinary('h_on_start')
binaryCode += binaryParser.getBinary('c_forever')
binaryCode += binaryParser.getBinary('set_status_light', {'color': 1})
binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 1})
binaryCode += binaryParser.getBinary('set_status_light', {'color': 0})
binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 1})
binaryCode += binaryParser.getBinary('c_end')

print("Binary code is: {}\n".format(binaryCode))

code = binaryParser.parse(binaryCode)

# pythonImpl = PythonCodeImpl()
pythonImpl = Ev3DevCodeImpl()
codeConverter = CodeConverter(pythonImpl)
code = codeConverter.convert(code)
codeConverter.display()

file = FileHandler('config.ini')
ssh = SshHandler('config.ini')

file.write(code)
ssh.sendFile()
ssh.executeCode()

try:
    while True:
        pass
except KeyboardInterrupt:
    ssh.stopCode()
    ssh.close()
