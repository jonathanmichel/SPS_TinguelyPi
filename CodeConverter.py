"""
Author: Jonathan Michel
Date:   22.12.2021
This class translates an array of functions that represent a Scratch program in a precise language.
A class implementing the CodeImpl interface has to be specified to
"""

from CodeImplementations.CodeImpl import CodeImpl
from util import *


class CodeConverter:
    def __init__(self, impl):
        if issubclass(type(impl), CodeImpl):
            self.impl = impl
        else:
            print("Impossible to convert code. Code implementation has to be a subclass of CodeImpl")
            exit()

    # Convert code provided as array
    def convert(self, code):
        error = False
        self.impl.clearCode()
        for c in code:
            args = convertArgumentArrayToList(c['args'])

            try:
                self.impl.debugLine(c['name'], args)
                function = 'self.impl.' + c['name'] + '(' + args + ')'
                # print(function)
                eval(function)
            except AttributeError:  # Implementation does not provide code for required function
                self.impl.missingImplementationHandler(c['name'], args)
                error = True
            except TypeError as e:  # Incorrect arguments list passed to the implementation
                print("/!\\ Error when converting {}, incorrect arguments for current implementation."
                      .format(c['name']))
                print(e)
                error = True
            except Exception as e:  # Another error occurred
                print("/!\\ Error when converting {}".format(c['name']))
                print("{} {}".format(type(e), e))
                error = True

        if error:
            return None

        return self.impl.getCode()

    def getCode(self):
        return self.impl.getCode()

    def display(self):
        print("=" * 15)
        print("Converted code with {}".format(self.impl.__class__.__name__))
        print("=" * 15)
        self.impl.display()
        print("=" * 15)

    def execute(self):
        self.impl.execute()
