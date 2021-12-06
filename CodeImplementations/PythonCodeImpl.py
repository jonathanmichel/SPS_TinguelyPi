import time
from CodeImplementations.CodeImpl import CodeImpl


class PythonCodeImpl(CodeImpl):
    def __init__(self):
        super().__init__()
        self.code = ''
        self.level = 0

    def clearCode(self):
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

    def missingImplementationHandler(self, block, args):
        self.addLine("# /!\\ Missing implementation for {}({})".format(block, args))

    def c_forever(self):
        self.addLine("while True:")
        self.level += 1

    def c_repeat(self, times):
        self.addLine("for i in range({}):".format(times))
        self.level += 1

    def c_repeat_until(self, boolean):
        super().boolean(self, boolean)
        self.addLine("while booleanCheck:")
        self.level += 1
        super().boolean(self, boolean)

    def c_if(self, boolean):
        super().boolean(self, boolean)
        self.addLine("if booleanCheck:")
        self.level += 1

    def c_else(self):
        self.level -= 1
        self.addLine("else:")
        self.level += 1

    def c_end(self):
        self.level -= 1

    def h_on_start(self):
        self.addLine("# [h_on_start]")

    def wait_seconds(self, seconds):
        self.addLine("time.sleep({})".format(seconds))

    def wait_until(self, boolean):
        self.addLine("# /// wait_until \\\\\\")
        self.addLine("booleanCheck = False")
        self.addLine("while not booleanCheck:")
        self.level += 1
        super().boolean(self, boolean)
        self.level -= 1
        self.addLine("# \\\\\\ wait_until /// ")

    def set_status_light(self, color):
        self.addLine("print('Set color to {}')".format(color))

    def b_touch(self, port):
        self.addLine("booleanCheck = False # b_touch {}".format(port))

    def b_distance(self, port, operator, value, unit):
        self.addLine("booleanCheck = False # b_distance {} {} {} {}".format(port, operator, value, unit))
