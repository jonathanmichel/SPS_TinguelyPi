import xml.etree.ElementTree as ET


class BinaryCodeParser:
    def __init__(self, path):
        self.path = path
        self.validXml = False

        try:
            self.tree = ET.parse(self.path)
            self.root = self.tree.getroot()

            info = self.root.find("info")
        except:
            print("Invalid xml, check file {}".format(self.path))
            return

        if info:
            try:
                self.version = info.find("version").text
                self.idSize = int(info.find("blockIdSize").text)

                self.validXml = True

                print("Schema {} loaded for V{}, block id size is {} bits".format(self.path, self.version, self.idSize))
            except:
                print("Invalid xml, specify version and blockIdSize tags in <info>: {}".format(self.path))

        else:
            print("Invalid xml, specify info tag in {}".format(self.path))


    @staticmethod
    def convertIntArrayToBinaryChain(int_array):
        binary_chain = ''
        for i in int_array:
            # Convert each element
            binary_chain += bin(i)[2:].zfill(8)
        return binary_chain

    @staticmethod
    def calculatePaddingSize(args_length):
        # Each function and its argument(s) are encoded in a given number of byte. Given the fact that
        # arguments could take any number of bits, we need to add zero-padding bits to ensure having a multiple
        # of 8 (bits) for the full encoded data.
        # Example:
        #   - [function ID, 8 bits][color, 3 bits] => 5 padding bits : 2 byte for full function
        #   - [function ID, 8 bits][ports, 2 bits][direction, 1 bit][value, 8 bits]
        #       => 5 padding bits : 3 bytes for full function
        paddingSize = 0
        if args_length % 8 != 0:
            paddingSize = 8 - (args_length % 8)
        return paddingSize

    def parse(self, binary):
        if not self.validXml:
            print("Unable to parse binary, invalid xml")
            return None

        if binary:
            print("Parsing binary code: {}".format(hex(int(binary, 2))))

            code = []

            while binary:
                # Get functionId and remove it from binary chain
                function_id = binary[0:self.idSize]
                binary = binary[self.idSize:]
                # Extract function and its arguments
                function_res = self.findNextFunction(int(function_id), binary)
                if function_res:
                    args_length = int(function_res['args_length'])

                    # Remove padding bits from binary chain in order to find the next function id
                    args_length += self.calculatePaddingSize(args_length)

                    # Remove arguments binary data from binary chain
                    binary = binary[args_length:]
                    code.append(function_res)

                    # print(function_res)
                else:
                    print("Error decoding binary chain")
                    return None

            return code
        else:
            print("Unable to parse binary, None chain")

    def findNextFunction(self, requestId, binaryCode):
        if not self.validXml:
            print("Unable to findNextFunction in binary, invalid xml")
            return None

        # print("Looking for 0b{} = {}".format(requestId, int(str(requestId), 2)))
        blocks = self.root.find("blocks")

        for block in blocks:
            # Get next function id in the binary chain
            id_hex = block.find("id").text
            id = int(id_hex, 0)

            # Find function id in xml description
            if id == int(str(requestId), 2):
                ret_args = []

                # Get argument required by found function
                args_length = 0
                args = block.find("arguments")

                if args:
                    for arg in args:
                        # Get number of bits required for current argument
                        arg_size = int(arg.attrib['size'])
                        # Count total number of bits for arguments
                        args_length += arg_size

                        # Get argument depending on size
                        ret_arg = {
                            'name': arg.tag,
                            'size': arg_size,
                            'type': arg.attrib['type'],
                            'value': binaryCode[0:arg_size]
                        }

                        # Remove current argument from local binary chain
                        binaryCode = binaryCode[arg_size:]

                        ret_args.append(ret_arg)

                ret = {
                    'id': id,
                    'block': block.attrib['name'],
                    'args_length': args_length,
                    'args': ret_args
                }

                # print(ret)

                return ret

        # If function was not found
        return None

    def getBinary(self, requestBlock, argsList=None):
        # Check that xml is correctly loaded
        if not self.validXml:
            print("Unable to getBinary(), invalid xml")
            return None

        blocks = self.root.find("blocks")

        if blocks is not None:
            # Parse all blocks in xml to find the requested block
            for block in blocks:
                if block.attrib['name'] == requestBlock:
                    # Extract id and convert it in binary
                    try:
                        id_hex = block.find("id").text
                        id_int = int(id_hex, 16)
                        id_bin = bin(id_int)[2:].zfill(self.idSize)
                    except AttributeError:
                        print("/!\\ getBinary() failed, please specify 'id' for '{}' in {}"
                              .format(requestBlock, self.path))
                        return None
                    except ValueError:
                        print("/!\\ getBinary() failed, incorrect 'id' value ({}) for '{}' in {}. Specify id in hex."
                              .format(id_hex, requestBlock, self.path))
                        return None

                    # Get arguments required according to xml definition
                    args = block.find("arguments")

                    ret_args = []
                    args_length = 0

                    if args:
                        for arg in args:
                            # Get type and bits size for each argument required according to xml definition
                            arg_name = arg.tag

                            try:
                                arg_size = int(arg.attrib['size'])
                                arg_type = arg.attrib['type']
                            except KeyError as e:
                                print("/!\\ getBinary() for '{}' failed. Please specify {} for argument '{}' in {}"
                                      .format(requestBlock, e, arg_name, self.path))
                                return None

                            # Get argument value passed to function
                            try:
                                arg_value = argsList[arg_name]
                            except KeyError:    # If arg is not found in argList
                                print("/!\\ getBinary() for '{}' failed. "
                                      "Please specify argument '{}' when calling function."
                                      .format(requestBlock, arg_name))
                                return None
                            except TypeError:   # If argList is empty
                                required_args = []
                                for arg in args:
                                    required_args.append(arg.tag)

                                print("/!\\ getBinary() for '{}' failed. "
                                      "Please specify arguments '{}' when calling function."
                                      .format(requestBlock, required_args))
                                return None

                            # Increment arguments bits size
                            args_length += arg_size

                            # Convert argument value to binary according to its type
                            try:
                                if arg_type == 'uint':
                                    val = bin(arg_value)[2:].zfill(arg_size)
                                    ret_args.append(val)
                                elif arg_type == 'enum':
                                    choices = []
                                    val = None

                                    for enum in arg:
                                        if enum.tag == 'enum':
                                            choices.append("{}".format(enum.text))
                                            if arg_value == enum.text:
                                              val = bin(int(enum.attrib['value']))[2:].zfill(arg_size)

                                    if val:
                                        ret_args.append(val)
                                    else:
                                        choices = ', '.join(choices)
                                        print("/!\\ getBinary() for '{}' failed. "
                                              "Invalid value ({}) for argument '{}'.\n According to {}, choices are: {}"
                                              .format(requestBlock, arg_value, arg_name, self.path, choices))
                                        return None
                                else:
                                    print("/!\\ getBinary() for '{}' failed. "
                                          "Invalid type ({}) for argument '{}' in {}"
                                          .format(requestBlock,  arg_type, arg_name, self.path))
                                    return None
                            except TypeError:
                                print("/!\\ getBinary() for '{}' failed. "
                                      "Unable to use '{}' as '{}' value as requested by argument '{}'"
                                      .format(requestBlock, arg_value, arg_type, arg_name))
                                return None

                    # Add padding
                    padding_size = self.calculatePaddingSize(args_length)
                    padding = '' + '0' * padding_size

                    ret = id_bin + ''.join(ret_args) + padding

                    # print("{} found: id={} ({}), args={}, padding={} bits. Code: {}".
                    #     format(requestBlock, id_hex, id_int, ret_args, padding_size, hex(int(ret, 2))))

                    return ret

            # If requested block was not found
            print("/!\\ Block {} not found in {}".format(requestBlock, self.path))
            return None

        # If blocks are not correctly defined in xml
        print("/!\\ Invalid {}, missing tag 'blocks'".format(self.path))
        return None
