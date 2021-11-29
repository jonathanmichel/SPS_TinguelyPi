
class CodeConverter:
    def __init__(self, impl):
        self.impl = impl

    # Convert code provided as array
    def convert(self, code):
        self.impl.clearCode()
        for c in code:
            args = []
            # Create parameters list for function evaluation below depending on arguments array
            for a in c['args']:
                arg_type = type(a['value'])
                if arg_type is str:
                    parameter = "{}='{}'"
                elif arg_type is int:
                    parameter = "{}={}"
                else:
                    print("/!\\ Non-supported type ({}: {}) when converting code for argument {}".
                          format(arg_type, a['value'], a['name']))
                    return None

                args.append(parameter.format(a['name'], a['value']))
            args = ','.join(args)

            print(args)

            try:
                eval('self.impl.' + c['block'] + '(' + args + ')')
            except AttributeError:  # Implementation does not provide code for required function
                self.impl.missingImplementationHandler(c['block'], args)
            except TypeError as e:  # Incorrect arguments list passed to the implementation
                print("/!\\ Error when converting {}, incorrect arguments for current implementation.".format(c['block']))
                print(e)
            except Exception as e:  # Another error occurred
                print("/!\\ Error when converting {}".format(c['block']))
                print("{} {}".format(type(e), e))
                exit()

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
