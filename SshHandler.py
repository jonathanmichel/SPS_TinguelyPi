import configparser
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


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
        self.sshClient.connect(self.ev3_ip, port=22, username=self.ev3_username)

    def sendFile(self):
        with SCPClient(self.sshClient.get_transport()) as scp:
            scp.put(self.main_file_name, self.ev3_deployment_path + self.main_file_name)
        print('File ' + self.main_file_name + ' sent to ' +
              self.ev3_username + '@' + self.ev3_ip + ':' + self.ev3_deployment_path)

    def executeCode(self):
        path = self.ev3_deployment_path + self.main_file_name
        print('Executing ' + self.ev3_ip + ':' + path)
        self.sshClient.exec_command('python3 ' + path)

    def stopCode(self):
        print('Code stopped')
        self.sshClient.exec_command(self.ev3_deployment_path + 'kill.sh')

    def close(self):
        self.sshClient.close()
