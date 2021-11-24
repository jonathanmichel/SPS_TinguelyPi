
class CodeConverter:
    def __init__(self, impl):
        self.impl = impl

    def convert(self, code):
        for c in code:
            args = []
            for a in c['args']:
                args.append("{}={}".format(a['name'], int(a['value'], 2)))
            args = ','.join(args)

            try:
                eval('self.impl.' + c['block'] + '(' + args + ')')
            except:
                self.impl.missingImplementationHandler(c['block'], args)

            """
            args = []
            for a in c['args']:
                args.append("{}={}".format(a['name'], int(a['value'], 2)))
            args = ','.join(args)
            print("{}({})".format(c['block'], args))
            """
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
