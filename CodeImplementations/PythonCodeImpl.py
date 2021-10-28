import time


class PythonCodeImpl:
    def __init__(self):
        self.code = ''
        self.level = 0

    def addLine(self, line):
        self.code += "{}{}\n".format(("\t" * self.level), line)

    def getCode(self):
        return self.code

    def display(self):
        print(self.code)

    def execute(self):
        print("Executing code ...")
        exec(self.code)

    def clear(self):
        self.code = ''

    def c_forever(self):
        self.addLine("while True:")
        self.level += 1

    def c_end(self):
        self.level -= 1

    def h_on_start(self):
        self.addLine("# [h_on_start]")

    def wait_seconds(self, seconds):
        self.addLine("time.sleep({})".format(seconds))

    def set_status_light(self, color):
        self.addLine("print('Set color to {}')".format(color))

