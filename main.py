#!/usr/bin/env python3
from BinaryCodeParser import *
from CodeConverter import *
from CodeImplementations.Ev3DevCodeImpl import *
from CodeImplementations.PythonCodeImpl import *


def toHex(hexStr):
    return hex(int(hexStr, 2))


# Load xmlParser
binaryParser = BinaryCodeParser('blocks.xml')

# Generate binary code
binaryCode = ''
binaryCode += binaryParser.getBinary('h_on_start')
binaryCode += binaryParser.getBinary('c_forever')
binaryCode += binaryParser.getBinary('set_status_light', {'color': 3})
binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 2})
binaryCode += binaryParser.getBinary('set_status_light', {'color': 4})
binaryCode += binaryParser.getBinary('set_status_light', {'color': 7})
binaryCode += binaryParser.getBinary('wait_seconds', {'seconds': 1})
binaryCode += binaryParser.getBinary('c_end')

print("Binary code is: {}\nDecoding ...".format(binaryCode))


code = binaryParser.parse(binaryCode)

# Convert code
print("Converted code")
print("-" * 15)

pythonImpl = PythonCodeImpl()
# pythonImpl = Ev3DevCodeImpl()
codeConverter = CodeConverter(pythonImpl)
codeConverter.convert(code)
codeConverter.display()
codeConverter.execute()
