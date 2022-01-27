import configparser
from paramiko import SSHClient, AutoAddPolicy, SSHException
from scp import SCPClient
import socket

class SshHandler:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.ev3_ip = config['EV3']['ip']
        self.ev3_username = config['EV3']['username']
        self.ev3_deployment_path = config['EV3']['deploymentPath']
        self.main_file_name = config['Code']['mainFileName']

        self.sshClient = SSHClient()
        self.sshClient.set_missing_host_key_policy(AutoAddPolicy())
        # Password less connection. Rsa public key from host (Pi) has to be added to
        # target (EV3) ssh folder : /home/[user]/.ssh/known_host
        print("Try to connect to the EV3 by SSH: {}@{} ...".format(self.ev3_username, self.ev3_ip))
        try:
            self.sshClient.connect(self.ev3_ip, port=22, username=self.ev3_username, timeout=2)
        except socket.timeout:
            print("\tUnable to connect to the EV3 by SHH")
            return
        except OSError as e:
            print("\tUnable to use SSH")
            print(e)
            return

        print("\tSSH connection to EV3 successful")

    def sendFile(self):
        with SCPClient(self.sshClient.get_transport()) as scp:
            scp.put(self.main_file_name, self.ev3_deployment_path + self.main_file_name)

        print('File ' + self.main_file_name + ' sent to ' +
              self.ev3_username + '@' + self.ev3_ip + ':' + self.ev3_deployment_path + self.main_file_name)

    def executeCode(self):
        path = self.ev3_deployment_path + self.main_file_name
        print('Executing ' + self.ev3_ip + ':' + path)
        self.sshClient.exec_command('brickrun ' + path)

    def stopCode(self):
        stdin, stdout, stderr = self.sshClient.exec_command(self.ev3_deployment_path + 'kill.sh')
        print('Code stopped (Status is {})'.format(stdout.channel.recv_exit_status()))

    def close(self):
        self.sshClient.close()
