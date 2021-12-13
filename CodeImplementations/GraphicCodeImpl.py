import time
from CodeImplementations.CodeImpl import CodeImpl
from CodeImplementations.AsciiDrawer import AsciiDrawer


class GraphicCodeImpl(CodeImpl):
    def __init__(self):
        super().__init__()
        self.asciiDrawer = AsciiDrawer(self)

    def clearCode(self):
        self.code = ''
        self.level = 0

    ###############################
    # CodeImpl functions
    ###############################

    def execute(self):
        print("No execution for Ev3DevCodeImpl")

    def missingImplementationHandler(self, block, args):
        print("/!\\ Please implement {}() in GraphicCodeImpl.py".format(block))
        self.asciiDrawer.drawStackBlock("[!] Missing implementation for {}({})".format(block, args))

    ###############################
    # C BLOCKS IMPLEMENTATIONS
    ###############################

    def c_end(self):
        self.level -= 1
        self.asciiDrawer.drawStackBlock(" " * (self.asciiDrawer.blockLength - 5) + "^", upNotchLevel=1, openRoof=True)

    def c_forever(self):
        self.asciiDrawer.drawStackBlock("forever", lowNotchLevel=1)
        self.level += 1

    def c_if(self, boolean):
        b = super().boolean(self, boolean)
        self.asciiDrawer.drawStackBlock("if < {} >".format(b), lowNotchLevel=1)
        self.level += 1

    def c_repeat(self, times):
        self.asciiDrawer.drawStackBlock("repeat {}".format(times), lowNotchLevel=1)
        self.level += 1

    def c_repeat_until(self, boolean):
        b = super().boolean(self, boolean)
        self.asciiDrawer.drawStackBlock("repeat until < {} >".format(b), lowNotchLevel=1)
        self.level += 1

    def c_else(self):
        self.level -= 1
        self.asciiDrawer.drawStackBlock("else:", openRoof=True, upNotchLevel=1)
        self.level += 1

    ###############################
    # H BLOCKS IMPLEMENTATIONS
    ###############################

    def h_on_start(self):
        self.asciiDrawer.drawHatBlock("when program starts")

    ###############################
    # STACK BLOCKS IMPLEMENTATIONS
    ###############################

    def motors_run_direction(self, port, direction, unit, value):
        self.asciiDrawer.drawStackBlock("({}) run [{}] for ({}) [{}]".format(port, direction, value, unit))

    def motors_start_speed(self, port, direction, speed):
        self.asciiDrawer.drawStackBlock("({}) start motor at ({}) % speed".format(port, speed))

    def motors_stop(self, port):
        self.asciiDrawer.drawStackBlock("({}) stop motor".format(port))

    def set_status_light(self, color):
        # Scratch colors : 0: off, 1: green, 2: red, 3: orange, 4: green pulse, 5: red pulse, 6: orange pulse
        # Ev3Python2 colors : 'RED', 'GREEN', 'YELLOW', 'ORANGE, 'AMBER', 'BLACK'
        supported_colors = ['BLACK', 'GREEN', 'RED', 'ORANGE']
        # Not supported : 'GREEN_PULSE', 'RED_PULSE', 'ORANGE_PULSE'

        color_ev3 = 'BLACK'
        if color in supported_colors:
            color_ev3 = color

        self.asciiDrawer.drawStackBlock("set status light to [{}]".format(color_ev3))

    def wait_seconds(self, seconds):
        self.asciiDrawer.drawStackBlock("wait ({}) seconds".format(seconds))

    def wait_touch(self, port, state):
        self.asciiDrawer.drawStackBlock("({}) wait until [{}]".format(port, state))

    def wait_until(self, boolean):
        b = super().boolean(self, boolean)
        self.asciiDrawer.drawStackBlock("wait until < {} >".format(b))

    ###############################
    # BOOLEAN IMPLEMENTATIONS
    ###############################

    def b_touch(self, port):
        return "({}) is pressed ?".format(port)

    def b_distance(self, port, operator, sign, value, unit):
        if sign == 'negative':
            value *= -1
        return "({}) is distance [{}] ({}) [{}]".format(port, operator, value, unit)
