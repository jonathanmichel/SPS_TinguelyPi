#!/usr/bin/env python3
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
binaryCode += binaryParser.getBinary('c_forever')
binaryCode += binaryParser.getBinary('wait_touch', {'port': 0, 'state': 0})
binaryCode += binaryParser.getBinary('motors_start_speed', {'port': 2, 'direction': 1, 'value': 20})
binaryCode += binaryParser.getBinary('wait_touch', {'port': 0, 'state': 1})
binaryCode += binaryParser.getBinary('motors_stop', {'port': 2})
binaryCode += binaryParser.getBinary('c_end')

# binaryCode += binaryParser.getBinary('motors_run_direction', {'port': 1, 'direction': 1, 'value': 180})
# binaryCode += binaryParser.getBinary('motors_start_speed', {'port': 2, 'direction': 1, 'value': 90})
# binaryCode += binaryParser.getBinary('motors_stop', {'port': 2})
# binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 1})
# binaryCode += binaryParser.getBinary('c_forever')
# binaryCode += binaryParser.getBinary('set_status_light', {'color': 1})
# binaryCode += binaryParser.getBinary('c_end')

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
