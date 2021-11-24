import time

"""
 ______________
/              \------------------------
| when program starts                  |
---     --------------------------------
   \___/
___     ________________________________
|  \___/                               |
| Wait (5) seconds                     |
---     --------------------------------
   \___/
   
Notch levels
0:
3 -> 5 (notch) -> tail 
___     ________________________________
|  \___/                               |
---     --------------------------------
   \___/

1: 
3 -> 5 (padding) -> 5 (notch) -> tail
________     ___________________________
|       \___/                          |
--------     ---------------------------
        \___/

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

    def clear(self):
        self.code = ''

    def missingImplementationHandler(self, block, args):
        self.addLine("# /!\\ Missing implementation for {}".format(block))

    def c_forever(self):
        self.drawStackBlock("forever", self.level, self.level + 1)
        self.level += 1

    def c_end(self):
        self.level -= 1
        self.drawStackBlock(" " * (self.blockLength - 5) + "^", self.level + 1, self.level)

    def h_on_start(self):
        self.drawHatBlock("when program starts")

    def wait_seconds(self, seconds):
        self.drawStackBlock("wait ({}) seconds".format(seconds))

    def set_status_light(self, color):
        self.drawStackBlock("set status light to [{}]".format(color))

    def removeLastBlockTail(self):
        if self.concatenateBlocks and self.code != '':
            self.code = "\n".join(self.code.split("\n")[:-3])
            self.code += "\n"

    def drawNotchLine(self, level):
        # ___     ________________________________
        self.addLine("____" +   # Block header
                     ("_" * self.notchSize) * level     # Potential block spacing
                     + (" " * self.notchSize)           # Notch empty zone
                     + (self.blockLength - 4 - (self.notchSize * level) - self.notchSize) * "_")    # Block end

    def drawUpperNotch(self, level):
        self.drawNotchLine(level)
        # |  \___/                               |
        self.addLine("|   " +
                     " " * self.levelShiftSize * level +
                     "\\__/" +
                     " " * (self.blockLength - self.notchSize - (self.levelShiftSize * level) - 4 - 1) +
                     "|")

    def drawLowerNotch(self, level):
        self.drawNotchLine(level)
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

    def drawStackBlock(self, functionText, upNotchLevel=0, lowNotchLevel=0):
        self.removeLastBlockTail()
        self.drawUpperNotch(upNotchLevel)
        self.addLine("| " + functionText + (self.blockLength - len(functionText) - 3) * " " + "|")
        self.drawLowerNotch(lowNotchLevel)






