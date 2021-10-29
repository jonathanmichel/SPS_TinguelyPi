import configparser


class FileHandler:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.main_file_name = config['Code']['mainFileName']

    def write(self, code):
        f = open(self.main_file_name, "w")
        f.write(code)
        f.close()
        print('File ' + self.main_file_name + ' written')