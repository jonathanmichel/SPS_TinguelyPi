import time
from CodeImplementations.CodeImpl import CodeImpl


class PythonCodeImpl(CodeImpl):
    def __init__(self):
        super().__init__()

    def addLine(self, line):
        self.code += "{}{}\n".format(("\t" * self.level), line)

    def clearCode(self):
        self.code = ''
        self.level = 0

    ###############################
    # CodeImpl functions
    ###############################

    def execute(self):
        print("Executing code ...")
        exec(self.code)

    def missingImplementationHandler(self, block, args):
        self.addLine("# /!\\ Missing implementation for {}({})".format(block, args))

    ###############################
    # C BLOCKS IMPLEMENTATIONS
    ###############################

    def c_end(self):
        self.level -= 1

    def c_forever(self):
        self.addLine("while True:")
        self.level += 1

    def c_if(self, boolean):
        self.addLine("# /// c_if \\\\\\")
        super().boolean(self, boolean)
        self.addLine("if booleanCheck:")
        self.addLine("# \\\\\\ c_if /// ")
        self.level += 1

    def c_repeat(self, times):
        self.addLine("for i in range({}):".format(times))
        self.level += 1

    def c_repeat_until(self, boolean):
        self.addLine("# /// c_repeat_until \\\\\\")
        super().boolean(self, boolean)
        self.addLine("while booleanCheck:")
        self.level += 1
        super().boolean(self, boolean)
        self.addLine("# \\\\\\ c_repeat_until /// ")

    def c_else(self):
        self.level -= 1
        self.addLine("else:")
        self.level += 1

    ###############################
    # H BLOCKS IMPLEMENTATIONS
    ###############################

    def h_on_start(self):
        self.addLine("# [h_on_start]")

    ###############################
    # STACK BLOCKS IMPLEMENTATIONS
    ###############################

    def motors_run_direction(self, port, direction, unit, value):
        self.addLine("print('motors_stop({}, {}, {}, {})')".format(port, direction, unit, value))

    def motors_start_speed(self, port, direction, speed):
        self.addLine("print('motors_stop({}, {}, {})')".format(port, direction, speed))

    def motors_stop(self, port):
        self.addLine("print('motors_stop({})')".format(port))

    def set_status_light(self, color):
        self.addLine("print('Set color to {}')".format(color))

    def wait_seconds(self, seconds):
        self.addLine("time.sleep({})".format(seconds))

    def wait_touch(self, port, state):
        self.addLine("print('wait_touch({}, {})')".format(port, state))

    def wait_until(self, boolean):
        self.addLine("# /// wait_until \\\\\\")
        self.addLine("booleanCheck = False")
        self.addLine("while not booleanCheck:")
        self.level += 1
        super().boolean(self, boolean)
        self.level -= 1
        self.addLine("# \\\\\\ wait_until /// ")

    ###############################
    # BOOLEAN IMPLEMENTATIONS
    ###############################

    def b_touch(self, port):
        self.addLine("booleanCheck = False # b_touch {}".format(port))

    def b_distance(self, port, operator, sign, value, unit):
        self.addLine("booleanCheck = False # b_distance {} {} {} {} {}".format(port, operator, sign, value, unit))
