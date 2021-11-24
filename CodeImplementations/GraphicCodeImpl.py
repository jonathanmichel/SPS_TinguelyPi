import time

"""
 ____________
/            \--------------------------
| when program starts                  |
|---    --------------------------------
|   \__/                               |
| forever                              |
|   |---    --------------------------------
|   |   \__/                               |
|   | wait (13) seconds                    |
|   |---    --------------------------------
|   |   \__/                               |
|   | set status light to [GREEN]          |
|   ----    ----------------------------
|       \__/                           |
|                                    ^ |
|___    ________________________________
    \__/

"""


class GraphicCodeImpl:
    def __init__(self):
        self.code = ''
        self.level = 0
        self.blockLength = 40
        self.levelShiftSize = 4
        self.notchSize = 4
        self.concatenateBlocks = True

    def addLine(self, line):
        level_indicator_unit = "|" + (self.levelShiftSize - 1) * " "
        level_indicator = level_indicator_unit * self.level
        self.code += "{}{}\n".format(level_indicator, line)

    def getCode(self):
        return self.code

    def display(self):
        print("=" * 15)
        print("Graphic representation of the converted code")
        print("=" * 15)
        print(self.code)
        print("=" * 15)

    def execute(self):
        print("No execution for Ev3DevCodeImpl")
        exit()

    def clear(self):
        self.code = ''

    def missingImplementationHandler(self, block, args):
        print("/!\\ Please implement {}() in GraphicCodeImpl.py".format(block))
        self.drawStackBlock("[!] Missing implementation for {}({})".format(block, args))
        #exit()

    def c_forever(self):
        self.drawStackBlock("forever", 0, 1)
        self.level += 1

    def c_end(self):
        self.level -= 1
        self.drawStackBlock(" " * (self.blockLength - 5) + "^", 1, 0, True)

    def h_on_start(self):
        self.drawHatBlock("when program starts")

    def wait_seconds(self, seconds):
        self.drawStackBlock("wait ({}) seconds".format(seconds))

    def set_status_light(self, color):
        # Scratch colors : 0: off, 1: green, 2: red, 3: orange, 4: green pulse, 5: red pulse, 6: orange pulse
        # Ev3Python2 colors : 'RED', 'GREEN', 'YELLOW', 'ORANGE, 'AMBER', 'BLACK'
        colors = ['BLACK', 'GREEN', 'RED', 'ORANGE', 'GREEN_PULSE', 'RED_PULSE', 'ORANGE_PULSE']
        color_int = int(color)

        color = colors[0]
        if 1 <= color_int <= 6:
            color = colors[color_int]

        self.drawStackBlock("set status light to [{}]".format(color))

    def removeLastBlockTail(self):
        if self.concatenateBlocks and self.code != '':
            self.code = "\n".join(self.code.split("\n")[:-3])
            self.code += "\n"

    def drawNotchLine(self, char, level, openRoof=False):
        # level = 0 :
        # |___     ________________________________
        # level = 1 : openRoof defines if there is spaces between the start of the text line and
        # the start of the notch line
        # |    ___     ____________________________
        #  /\ here
        # @todo Improve. Way too complidated. For c_end, openRoof is way too dirty
        block_begin = "|" + char * (self.levelShiftSize - 1)
        if openRoof:
            block_begin = "|" + (self.levelShiftSize - 1) * " " + (level - 1) * " " * (self.levelShiftSize - 2)

        endNb = self.blockLength - len(block_begin) - (self.notchSize * level) - self.notchSize
        self.addLine(block_begin
                        + (char * self.notchSize) * level  # Potential block spacing
                        + (" " * self.notchSize)           # Notch empty zone
                        + endNb * char)                     # Block end

    def drawUpperNotch(self, level, openRoof=False):
        self.drawNotchLine("-", level, openRoof)
        # |  \___/                               |
        self.addLine("|   " +
                     " " * self.levelShiftSize * level +
                     "\\__/" +
                     " " * (self.blockLength - self.notchSize - (self.levelShiftSize * level) - 4 - 1) +
                     "|")

    def drawLowerNotch(self, level):
        self.drawNotchLine("_", level)
        #     \___/                              |
        self.addLine("    " +
                     (" " * self.notchSize) * level +
                     "\\__/")

    def drawHatTop(self):
        hat_size = 12
        self.addLine(" " + hat_size * "_")
        self.addLine("/" + hat_size * " " + "\\" + "-" * (self.blockLength - hat_size - 2))

    def drawHatBlock(self, functionText):
        self.drawHatTop()
        self.addLine("| " + functionText + (self.blockLength - len(functionText) - 3) * " " + "|")
        self.drawLowerNotch(0)

    def drawStackBlock(self, functionText, upNotchLevel=0, lowNotchLevel=0, openRoof=False):
        self.removeLastBlockTail()
        self.drawUpperNotch(upNotchLevel, openRoof)
        self.addLine("| " + functionText + (self.blockLength - len(functionText) - 3) * " " + "|")
        self.drawLowerNotch(lowNotchLevel)






