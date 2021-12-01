# Create parameters list for function evaluation below depending on arguments array
def convertArgumentArrayToList(argumentArray):
    args = []
    for a in argumentArray:
        arg_type = type(a['value'])
        if arg_type is str:
            parameter = "{}='{}'"
        elif arg_type is int:
            parameter = "{}={}"
        elif arg_type is dict:
            parameter = "{}={}"
        else:
            print("/!\\ Non-supported type ({}: {}) when converting code for argument {}".
                  format(arg_type, a['value'], a['name']))
            return None

        args.append(parameter.format(a['name'], a['value']))

    args = ','.join(args)

    return args