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
        # Each block and its argument(s) are encoded in a given number of byte. Given the fact that
        # arguments could take any number of bits, we need to add zero-padding bits to ensure having a multiple
        # of 8 (bits) for the full encoded data.
        # Example:
        #   - [block, 8 bits][color, 3 bits] => 5 padding bits : 2 byte for full block
        #   - [block ID, 8 bits][ports, 2 bits][direction, 1 bit][value, 8 bits]
        #       => 5 padding bits : 3 bytes for full block
        paddingSize = 0
        if args_length % 8 != 0:
            paddingSize = 8 - (args_length % 8)
        return paddingSize

    def parse(self, binary):
        if not self.validXml:
            print("Unable to parse binary, invalid xml")
            return None

        res = self.checkBinary(binary)
        if res > 0:
            print("Converting binary {}".format(hex(int(binary, 2))))
        else:
            print("Unable to parse binary, chain is empty")
            return None

        code = []

        while binary:
            # Extract blocks and its arguments
            (binary, block) = self.decodeBlock(binary)

            if block:
                code.append(block)
            else:
                print("Error decoding binary chain")
                return None

        print("\tSuccessfully converted in {} line(s) of code".format(len(code)))

        return code

    def decodeBlock(self, binaryCode):
        if not self.validXml:
            print("Unable to decode block in binary, invalid xml")
            return None, None

        # Get blockId and remove it from binary chain
        block_id_bin = binaryCode[0:self.idSize]
        block_id = int(str(block_id_bin), 2)

        # print("Trying to decode block {} in {}".format(hex(block_id), hex(int(binaryCode, 2))))

        # Remove block id from binary chain
        binaryCode = binaryCode[self.idSize:]

        # Get all blocks (functions) in xml definition
        blocks = self.root.find("blocks")

        # Parse all blocks to find the required one
        for block in blocks:
            # For each of them, get block id
            id_hex = block.find("id").text
            id = int(id_hex, 0)

            # Test if block id corresponds to the required one
            if id == block_id:
                # Get argument required by block according to xml
                args = block.find("arguments")

                (ret_args, binaryCode) = self.decodeArguments(args, binaryCode)

                # Construction block object to return
                block = {
                    'id': id,
                    'block': block.attrib['name'],
                    'args': ret_args
                }

                # print("\Block found: {}".format(block))

                return binaryCode, block

        print("Unable to decode block {}".format(hex(block_id)))

        # If block was not found
        return None, None

    def decodeBoolean(self, binaryCode):
        if not self.validXml:
            print("Unable to decode boolean in binary, invalid xml")
            return None

        # Get boolean id in binary chain
        boolean_id = int(binaryCode[0:self.idSize], 2)

        # print("Trying to decode boolean {} in {}".format(hex(boolean_id), hex(int(binaryCode, 2))))

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

                # print("\tBoolean found: {}".format(ret))

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

                # print("\tArgument found: {} - type: {}, size: {}, value: {}"
                #       .format(arg.tag, arg_type, arg_size, arg_value))

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
                    # already removed from binary chain by the current block

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

            # Remove padding bits from binary chain in order to find the next block id
            padding = self.calculatePaddingSize(args_length)

            # Remove arguments binary data from binary chain
            binaryCode = binaryCode[padding:]

            return ret_args, binaryCode

        # If there is no argument
        return [], binaryCode

    def encodeBlock(self, blockName, argsList=None):
        return self.encode("blocks", blockName, argsList)

    def encodeBoolean(self, booleanName, argsList=None):
        binary = self.encode("booleans", booleanName, argsList)

        if bin:
            length = len(binary)
            length_bin = bin(length)[2:].zfill(8)  # Encode length in 8 bits
            return length_bin + binary

        return None

    # Elements can be "blocks" or "booleans"
    def encode(self, elements, elementName, argsList=None):
        # Check that xml is correctly loaded
        if not self.validXml:
            print("Unable to encode, invalid xml")
            return None

        elements = self.root.find(elements)

        if elements is not None:
            # Parse all elements (blocks or booleans) in xml to find the requested one
            for element in elements:
                if element.attrib['name'] == elementName:
                    # Extract id and convert it in binary
                    try:
                        id_hex = element.find("id").text
                        id_int = int(id_hex, 16)
                        id_bin = bin(id_int)[2:].zfill(self.idSize)
                    except AttributeError as e:
                        print("/!\\ Encoding failed, please specify 'id' for '{}' in {}"
                              .format(elementName, self.path))
                        print(e)
                        return None
                    except ValueError:
                        print("/!\\ Encoding failed, incorrect 'id' value ({}) for '{}' in {}. "
                              "Specify id in hex."
                              .format(id_hex, elementName, self.path))
                        return None

                    # Get arguments required according to xml definition
                    args = element.find("arguments")

                    arguments_binary = self.encodeArguments(args, elementName, argsList)

                    if arguments_binary is not None:
                        ret = id_bin + arguments_binary
                    else:
                        return None

                    # print("{} found: id={} ({}), args={}, padding={} bits. Code: {}".
                    #     format(requestBlock, id_hex, id_int, ret_args, padding_size, hex(int(ret, 2))))

                    return ret

            # If requested element was not found
            print("/!\\ Encoding failed. '{}' not found in {}".format(elementName, self.path))
            return None

        # If elements (blocks or booleans) are not correctly defined in xml
        print("/!\\ Invalid {}, missing tag '{}'".format(elements, self.path))
        return None

    def encodeArguments(self, argsXml, elementName, argsList):
        ret_args = []
        args_length = 0

        if argsXml:
            # Parse all arguments for a specific element
            for arg_xml in argsXml:
                # Get type and bits size for each argument required according to xml definition
                argument = {'name': arg_xml.tag}

                # Get argument value passed to element
                try:
                    argument['value'] = argsList[argument['name']]
                except KeyError:  # If arg is not found in argList
                    print("/!\\ Argument encoding for '{}' failed. "
                          "Please specify argument '{}' when calling encoding function."
                          .format(elementName, argument['name']))
                    return None
                except TypeError:  # If argList is empty
                    required_args = []
                    for a in argsXml:
                        required_args.append(a.tag)

                    print("/!\\ Argument encoding for '{}' failed. "
                          "Please specify arguments '{}' when calling encoding function."
                          .format(elementName, required_args))
                    return None

                # Get argument size, if argument is binary calculate its length
                try:
                    argument['type'] = arg_xml.attrib['type']
                    if argument['type'] == 'binary':
                        size = self.checkBinary(argument['value'])
                        if size > 0:
                            argument['size'] = size
                        else:
                            print("/!\\ Argument encoding for '{}' failed. "
                                  "Incorrect binary value '{}' for argument '{}'"
                                  .format(elementName, argument['value'], argument['name'], self.path))
                            return None
                    else:
                        argument['size'] = int(arg_xml.attrib['size'])
                except KeyError as e:
                    print("/!\\ Argument encoding for '{}' failed. "
                          "Please specify {} for argument '{}' in {}"
                          .format(elementName, e, argument['name'], self.path))
                    return None

                # Increment arguments bits size
                args_length += argument['size']

                # Convert argument value to binary according to its type
                arg_binary = self.encodeArgument(argument, arg_xml, elementName=elementName)
                if arg_binary is not None:
                    ret_args.append(arg_binary)
                else:
                    return None

        # Add padding
        padding_size = self.calculatePaddingSize(args_length)
        padding = '' + '0' * padding_size

        ret = ''.join(ret_args) + padding

        return ret

    # Convert value to binary chain according to argument type
    def encodeArgument(self, argument, argumentXml, elementName='not-defined'):
        try:
            if argument['type'] == 'uint':
                return bin(argument['value'])[2:].zfill(argument['size'])
            elif argument['type'] == 'enum':
                choices = []
                val = None

                for enum in argumentXml:
                    if enum.tag == 'enum':
                        choices.append("{}".format(enum.text))
                        if argument['value'] == enum.text:
                            val = bin(int(enum.attrib['value']))[2:].zfill(argument['size'])

                if val:
                    return val
                else:
                    choices = ', '.join(choices)
                    print("/!\\ Argument encoding for '{}' failed. "
                          "Invalid value ({}) for argument '{}'.\n According to {}, choices are: {}"
                          .format(elementName, argument['value'], argument['name'], self.path, choices))
                    return None
            elif argument['type'] == 'binary':
                return argument['value']
            else:
                print("/!\\ Argument encoding for '{}' failed. "
                      "Invalid type ({}) for argument '{}' in {}"
                      .format(elementName, type, argument['name'], self.path))
                return None
        except TypeError:
            print("/!\\ Argument encoding for '{}' failed. "
                  "Unable to use '{}' as '{}' value as requested by argument '{}'"
                  .format(elementName, argument['value'], type, argument['name']))
            return None

    # Check that chain is a correct binary chain and returns its length
    @staticmethod
    def checkBinary(chain):
        try:
            int(chain, 2)
        except ValueError:
            return 0
        except TypeError:
            return 0

        return len(chain)