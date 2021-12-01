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
                self.idSize = int(info.find("idSize").text)

                self.validXml = True

                print("Schema {} loaded for V{}, block id size is {} bits".format(self.path, self.version, self.idSize))
            except:
                print("Invalid xml, specify version and idSize tags in <info>: {}".format(self.path))

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
            code = []

            while binary:
                # Extract function and its arguments
                (binary, function) = self.decodeFunction(binary)

                if function:
                    code.append(function)
                else:
                    print("Error decoding binary chain")
                    return None

            return code
        else:
            print("Unable to parse binary, chain is empty")

    def decodeFunction(self, binaryCode):
        if not self.validXml:
            print("Unable to decode function in binary, invalid xml")
            return None, None

        # Get functionId and remove it from binary chain
        function_id_bin = binaryCode[0:self.idSize]
        function_id = int(str(function_id_bin), 2)

        print("Trying to decode function {} in {}".format(hex(function_id), hex(int(binaryCode, 2))))

        # Remove function id from binary chain
        binaryCode = binaryCode[self.idSize:]

        # Get all blocks (functions) in xml definition
        blocks = self.root.find("blocks")

        # Parse all blocks to find the required one
        for block in blocks:
            # For each of them, get function id
            id_hex = block.find("id").text
            id = int(id_hex, 0)

            # Test if function id corresponds to the required one
            if id == function_id:
                # Get argument required by function according to xml
                args = block.find("arguments")

                (ret_args, binaryCode) = self.decodeArguments(args, binaryCode)

                # Construction function object to return
                function = {
                    'id': id,
                    'block': block.attrib['name'],
                    'args': ret_args
                }

                print("\tFunction found: {}".format(function))

                return binaryCode, function

        print("Unable to decode function {}".format(hex(function_id)))

        # If function was not found
        return None, None

    def decodeBoolean(self, binaryCode):
        if not self.validXml:
            print("Unable to decode boolean in binary, invalid xml")
            return None

        # Get boolean id in binary chain
        boolean_id = int(binaryCode[0:self.idSize], 2)

        print("Trying to decode boolean {} in {}".format(hex(boolean_id), hex(int(binaryCode, 2))))

        # Remove boolean id from binary chain
        binaryCode = binaryCode[self.idSize:]

        booleans = self.root.find("booleans")

        for bool in booleans:
            # Get boolean id
            id_hex = bool.find("id").text
            id = int(id_hex, 0)

            # Test if boolean id corresponds to the required one
            if id == boolean_id:
                # Get argument required by boolean according to xml
                args = bool.find("arguments")

                (ret_args, binaryCode) = self.decodeArguments(args, binaryCode)

                # Construction boolean object to return
                ret = {
                    'id': id,
                    'name': bool.attrib['name'],
                    'args': ret_args
                }

                print("\tBoolean found: {}".format(ret))

                return binaryCode, ret

        print("Unable to decode boolean {}".format(hex(boolean_id)))

        # If boolean was not found
        return None, None

    def decodeArguments(self, arguments, binaryCode):
        ret_args = []
        args_length = 0

        if arguments:
            for arg in arguments:
                arg_type = arg.attrib['type']

                # if argument is a binary chain (used for boolean), the size is
                # defined by the next byte, otherwise argument size is specified in xml definition
                if arg_type == 'binary':
                    arg_size = int(binaryCode[0:self.idSize], 2)
                    binaryCode = binaryCode[self.idSize:]
                else:
                    arg_size = int(arg.attrib['size'])

                # Get argument value and convert it according to its type
                arg_value = binaryCode[0:arg_size]

                print("\tArgument found: {} - type: {}, size: {}, value: {}"
                      .format(arg.tag, arg_type, arg_size, arg_value))

                if arg_type == 'uint':  # Convert binary value to int
                    arg_value = int(arg_value, 2)
                elif arg_type == 'enum':  # Convert binary value to enum str
                    enum_value = int(arg_value, 2)  # Convert binary to enum value (int)
                    arg_value = 'N/A'  # Default str if enum value is invalid
                    for enum in arg:
                        # Check if value is available in enum
                        if enum_value == int(enum.attrib['value']):
                            arg_value = enum.text
                            break
                elif arg_type == 'binary':  # Convert binary value to boolean or reporter
                    (_, arg_value) = self.decodeBoolean(arg_value)
                    # We do not use binary chain returned by decodeBoolean() because bits are
                    # already removed from binary chain by the current function

                # Count total number of bits for arguments
                args_length += arg_size

                # Construct arguments array
                ret_arg = {
                    'name': arg.tag,
                    # 'size': arg_size,
                    # 'type': arg_type,
                    'value': arg_value
                }
                ret_args.append(ret_arg)

                # Remove current argument from local binary chain
                binaryCode = binaryCode[arg_size:]

            # Remove padding bits from binary chain in order to find the next function id
            padding = self.calculatePaddingSize(args_length)

            # Remove arguments binary data from binary chain
            binaryCode = binaryCode[padding:]

            return ret_args, binaryCode

        # If there is no argument
        return [], binaryCode

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
                    except AttributeError as e:
                        print("/!\\ getBinary() failed, please specify 'id' for '{}' in {}"
                              .format(requestBlock, self.path))
                        print(e)
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
                                arg_type = arg.attrib['type']
                                if arg_type == 'binary':
                                    arg_size = 24  # @todo Variable length
                                else:
                                    arg_size = int(arg.attrib['size'])
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
                                elif arg_type == 'binary':
                                    ret_args.append(arg_value)
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
            print("/!\\ Block '{}' not found in {}".format(requestBlock, self.path))
            return None

        # If blocks are not correctly defined in xml
        print("/!\\ Invalid {}, missing tag 'blocks'".format(self.path))
        return None
