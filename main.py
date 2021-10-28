#!/usr/bin/env python3
import time
import sys
import signal
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from BinaryCodeParser import *
from CodeConverter import *
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

main_file_name = 'mainEv3Dev.py'
ev3_ip = '10.42.0.45'
ev3_deployment_path = '/home/robot/tinguely/'

f = open(main_file_name, "w")
f.write(code)
f.close()

print('File ' + main_file_name + ' written')

print('Send ' + main_file_name + ' file to ' + ev3_ip + ':' + ev3_deployment_path)

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect(ev3_ip, port=22, username='robot', password='maker')

with SCPClient(ssh.get_transport()) as scp:
    scp.put(main_file_name, ev3_deployment_path + main_file_name)

print('Execute ' + ev3_ip + ':' + ev3_deployment_path + main_file_name)
ssh.exec_command('python3 ' + ev3_deployment_path + main_file_name)

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Kill program')
    ssh.exec_command(ev3_deployment_path + 'kill.sh')
    ssh.close()

# codeConverter.execute()

