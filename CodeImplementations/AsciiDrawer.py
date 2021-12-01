class AsciiDrawer:
    def __init__(self, codeImpl):
        self.blockLength = 55
        self.levelShiftSize = 4
        self.notchSize = 4
        self.concatenateBlocks = True
        self.codeImpl = codeImpl

    def addLine(self, line):
        level_indicator_unit = "|" + (self.levelShiftSize - 1) * " "
        level_indicator = level_indicator_unit * self.codeImpl.level
        self.codeImpl.code += "{}{}\n".format(level_indicator, line)

    def removeLastBlockTail(self):
        if self.concatenateBlocks and self.codeImpl.code!= '':
            self.codeImpl.code = "\n".join(self.codeImpl.code.split("\n")[:-3])
            self.codeImpl.code += "\n"

    def drawNotchLine(self, char, level, openRoof=False):
        # level = 0 :
        # |___     ________________________________
        # level = 1 : openRoof defines if there is spaces between the start of the text line and
        # the start of the notch line
        # |    ___     ____________________________
        #  /\ here
        # @todo Improve. Way too complicated. For c_end, openRoof is way too dirty
        block_begin = "|" + char * (self.levelShiftSize - 1)
        if openRoof:
            block_begin = "|" + (self.levelShiftSize - 1) * " " + (level - 1) * " " * (self.levelShiftSize - 2)

        endNb = self.blockLength - len(block_begin) - (self.notchSize * level) - self.notchSize
        self.addLine(block_begin
                     + (char * self.notchSize) * level  # Potential block spacing
                     + (" " * self.notchSize)  # Notch empty zone
                     + endNb * char)  # Block end

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
