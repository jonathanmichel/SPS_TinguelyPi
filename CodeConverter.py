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
        self.impl.clearCode()
        for c in code:
            args = convertArgumentArrayToList(c['args'])

            try:
                function = 'self.impl.' + c['block'] + '(' + args + ')'
                # print(function)
                eval(function)
            except AttributeError:  # Implementation does not provide code for required function
                self.impl.missingImplementationHandler(c['block'], args)
            except TypeError as e:  # Incorrect arguments list passed to the implementation
                print("/!\\ Error when converting {}, incorrect arguments for current implementation."
                      .format(c['block']))
                print(e)
            except Exception as e:  # Another error occurred
                print("/!\\ Error when converting {}".format(c['block']))
                print("{} {}".format(type(e), e))
                exit()

        return self.impl.getCode()

    def getCode(self):
        self.impl.getCode()

    def display(self):
        print("=" * 15)
        print("Converted code with {}".format(self.impl.__class__.__name__))
        print("=" * 15)
        self.impl.display()
        print("=" * 15)

    def execute(self):
        self.impl.execute()
