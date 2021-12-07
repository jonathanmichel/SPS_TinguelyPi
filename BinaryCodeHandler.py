import xml.etree.ElementTree as ET
from math import *

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
        padding_size = 0
        if args_length % 8 != 0:
            padding_size = 8 - (args_length % 8)
        return padding_size

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

    # Elements can be "blocks" or "booleans"
    def decode(self, rootElement, binaryCode):
        if not self.validXml:
            print("Decoding failed, invalid xml")
            return None, None

        # Get element id in binary chain
        element_id_bin = binaryCode[0:self.idSize]
        element_id = int(str(element_id_bin), 2)

        # print("Trying to decode {} {} in {}".format(rootElement, hex(element_id), hex(int(binaryCode, 2))))

        # Remove boolean id from binary chain
        binaryCode = binaryCode[self.idSize:]

        elements = self.root.find(rootElement)

        # Parse all elements to find the required one
        for element in elements:
            # For each of them, get id
            id_hex = element.find("id").text
            id = int(id_hex, 0)

            # Test if element id corresponds to the required one
            if id == element_id:
                # Get argument required by element according to xml
                args = element.find("arguments")

                (ret_args, binaryCode) = self.decodeArguments(args, binaryCode)

                # Construction element object to return
                ret = {
                    'id': id,
                    'name': element.attrib['name'],
                    'args': ret_args
                }

                # print("\Element found in {}: {}".format(rootElement, ret))

                return binaryCode, ret

        print("Decoding failed for {}".format(hex(element_id)))

        # If element was not found
        return None, None

    def decodeBlock(self, binaryCode):
        return self.decode("blocks", binaryCode)

    def decodeBoolean(self, binaryCode):
        return self.decode("booleans", binaryCode)

    def decodeArguments(self, arguments, binaryCode):
        ret_args = []
        args_length = 0

        if arguments:
            for arg in arguments:
                arg_type = arg.attrib['type']

                # if argument is a binary chain (used for boolean), the size (in bytes) is
                # defined by the next byte, otherwise argument size (in bits) is specified in xml definition
                if arg_type == 'binary':
                    arg_size = int(binaryCode[0:self.idSize], 2) * 8
                    binaryCode = binaryCode[self.idSize:]
                else:
                    arg_size = int(arg.attrib['size'])

                # Get argument value and convert it according to its type
                arg_value = binaryCode[0:arg_size]

                arg_value = self.decodeArgumentValue(arg_type, arg_value, arg)

                # print("\tArgument found: {} - type: {}, size: {}, value: {}"
                #       .format(arg.tag, arg_type, arg_size, arg_value))

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

    def decodeArgumentValue(self, argType, argValue, argumentsXml):
        arg_value = None
        if argType == 'uint':  # Convert binary value to int
            arg_value = int(argValue, 2)
        elif argType == 'enum':  # Convert binary value to enum str
            enum_value = int(argValue, 2)  # Convert binary to enum value (int)
            arg_value = 'N/A'  # Default str if enum value is invalid
            for enum in argumentsXml:
                # Check if value is available in enum
                if enum_value == int(enum.attrib['value']):
                    arg_value = enum.text
                    break
        elif argType == 'binary':  # Convert binary value to boolean or reporter
            (_, arg_value) = self.decodeBoolean(argValue)
            # We do not use binary chain returned by decodeBoolean() because bits are
            # already removed from binary chain by the current block

        return arg_value

    # rootElement can be "blocks" or "booleans"
    def encode(self, rootElement, elementName, argsList=None):
        # Check that xml is correctly loaded
        if not self.validXml:
            print("Unable to encode, invalid xml")
            return None

        elements = self.root.find(rootElement)

        if elements is not None:
            # Parse all elements (blocks or booleans) in xml to find the requested one
            for element in elements:
                try:
                    current_element_name = element.attrib['name']
                    if current_element_name == elementName:
                        # Extract id and convert it in binary
                        id_hex = element.find("id").text
                        id_int = int(id_hex, 16)
                        id_bin = bin(id_int)[2:].zfill(self.idSize)

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

                except KeyError as e:  # When element.attrib['name'] fails
                    print("/!\\ Encoding failed, please specify attribute {} for '{}' in {}"
                          .format(e, elementName, self.path))
                    return None

                except AttributeError as e:  # When element.find("id").text
                    print("/!\\ Encoding failed, please specify tag 'id' for '{}' in {}"
                          .format(elementName, self.path))
                    print(e)
                    return None

                except ValueError:
                    print("/!\\ Encoding failed, incorrect 'id' value ({}) for '{}' in {}. "
                          "Specify id in hex."
                          .format(id_hex, elementName, self.path))
                    return None

            # If requested element was not found
            print("/!\\ Encoding failed. '{}' not found in {}".format(elementName, self.path))
            return None

        # If elements (blocks or booleans) are not correctly defined in xml
        print("/!\\ Invalid {}, missing tag '{}'".format(elements, self.path))
        return None

    def encodeBlock(self, blockName, argsList=None):
        return self.encode("blocks", blockName, argsList)

    def encodeBoolean(self, booleanName, argsList=None):
        binary = self.encode("booleans", booleanName, argsList)

        if bin:
            # Booleans are preceded by one byte that indicates boolean binary size in bytes
            bits_length = len(binary)
            bytes_length = ceil(bits_length / 8)

            # Encode length in on byte
            length_bin = bin(bytes_length)[2:].zfill(8)
            return length_bin + binary

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
                arg_binary = self.encodeArgumentValue(argument, arg_xml, elementName=elementName)
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
    def encodeArgumentValue(self, argument, argumentsXml, elementName='not-defined'):
        try:
            if argument['type'] == 'uint':
                return bin(argument['value'])[2:].zfill(argument['size'])
            elif argument['type'] == 'enum':
                choices = []
                val = None

                for enum in argumentsXml:
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
