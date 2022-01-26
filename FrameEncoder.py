"""
Author: Jonathan Michel
Date:   26.01.2022
This class encodes a string that represents the frame that could be received from the Arduino blocks. It is used to
allow adding lines to a received frame or debug the program behaviour without using the Arduinos.
This frame represents a Scratch program with each block having a unique id and a  pre-defined list of parameters.
The protocol is specified in an XML file that has to be passed to the constructor, see the documentation for
additional information.
"""
import xml.etree.ElementTree as ET


class FrameEncoder:
    def __init__(self, path):
        self.path = path
        self.validXml = False
        self.frame = ''

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

                print("Schema {} loaded for V{}, block id size is {} chars (max value 0x{})".
                      format(self.path, self.version, self.idSize, 'F' * self.idSize))
            except:
                print("Invalid xml, specify version and idSize tags in <info>: {}".format(self.path))

        else:
            print("Invalid xml, specify info tag in {}".format(self.path))

    def resetFrame(self):
        self.frame = ''

    def get(self):
        if len(self.frame) > 0:
            return self.frame[:-1]  # remove last '|' added by appendBlock
        return self.frame

    def print(self):
        print(self.get())

    def appendBlock(self, blockName, argsList=None):
        block = self.encodeBlock(blockName, argsList)
        if block:
            self.frame += block + '|'
        else:
            print("Unable to append block")

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
                        # Extract id and convert it in Ascii
                        id_hex = element.find("id").text  # xml definition has to define id in hex
                        if id_hex[:2] == "0x":
                            id_hex = id_hex[2:]     # remove 0x if user entered it

                        id_int = int(id_hex, 16)    # check that id is a number defined in hex

                        # Ensure id uses correct number of chars
                        id_hex = id_hex.zfill(self.idSize)

                        # Check that hex representation respects maximum allowed size fot the id
                        if len(id_hex) > self.idSize:
                            print("Unable to encode ! Invalid id ({}) for '{}'. Maximum value is 0x{}, "
                                  "increment hex id size in '{}'"
                                  .format(id_int, elementName, 'F' * self.idSize, self.path))
                            return None

                        # Get arguments required according to xml definition
                        args = element.find("arguments")

                        arguments = self.encodeArguments(args, elementName, argsList)

                        if arguments is not None:
                            ret = id_hex + arguments
                        else:
                            return None

                        return ret

                except KeyError as e:  # When element.attrib['name'] fails
                    print("/!\\ Encoding failed, please specify attribute {} for '{}' in {}"
                          .format(e, elementName, self.path))
                    return None

                except AttributeError as e:  # When element.find("id").text fails
                    print("/!\\ Encoding failed, please specify tag 'id' for '{}' in {}"
                          .format(elementName, self.path))
                    print(e)
                    return None

                except ValueError as e:  # When id is not specified in hex
                    print(e)
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
        boolean = self.encode("booleans", booleanName, argsList)

        if boolean:
            # Booleans are preceded by one char that indicates boolean binary in hex
            bin_length = len(boolean)

            # Encode length with one char
            if bin_length > 0xF:
                print("Unable to encode {}. Boolean too big, size can not be encoded in two chars."
                      .format(booleanName))
                return None

            # Remove '0x' and concatenate with boolean
            return str(hex(bin_length))[2:] + boolean

        return None

    def encodeArguments(self, argsXml, elementName, argsList):
        ret_args = []

        if argsXml:
            # Parse all arguments for a specific element
            for arg_xml in argsXml:
                # Get type and byte size for each argument required according to xml definition
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
                        # If argument type is binary, calculate its size
                        if argument['value']:
                            size = len(argument['value'])
                            argument['size'] = size
                        else:  # if value is None or empty
                            print("/!\\ Argument encoding for '{}' failed. "
                                  "Please specify valid binary for argument '{}'"
                                  .format(elementName, argument['name']))
                            return None
                    else:
                        argument['size'] = int(arg_xml.attrib['size'])
                except KeyError as e:
                    print("/!\\ Argument encoding for '{}' failed. "
                          "Please specify {} for argument '{}' in {}"
                          .format(elementName, e, argument['name'], self.path))
                    return None

                # Convert argument value to binary according to its type
                arg_binary = self.encodeArgumentValue(argument, arg_xml, elementName=elementName)
                if arg_binary is not None:
                    ret_args.append(arg_binary)
                else:
                    return None

        ret = ''.join(ret_args)

        return ret

    # Convert value to binary chain according to argument type
    def encodeArgumentValue(self, argument, argumentsXml, elementName='not-defined'):
        try:
            if argument['type'] == 'uint':

                # Get str representation of the value
                val_str = str(int(argument['value']))
                if len(val_str) > argument['size']:
                    print("Unable to encode argument {}, '{}' can not be represented in a string with {} chars. "
                          "Check argument size in .xml definition"
                          .format(argument['name'], argument['value'], argument['size']))
                    return None

                # Give correct size to string representation
                val_str = val_str.zfill(argument['size'])

                return val_str
            elif argument['type'] == 'enum':
                choices = []
                val = None

                for enum in argumentsXml:
                    if enum.tag == 'enum':
                        choices.append("{}".format(enum.text))
                        if argument['value'] == enum.text:
                            enum_value = enum.attrib['value']
                            if len(enum_value) != argument['size']:
                                print("/!\\ Argument encoding for '{}' failed. "
                                      "Argument '{}' is supposed to be {} byte(s) long, "
                                      "current value ({}) does not correspond. Check {}"
                                      .format(elementName, argument['name'],  argument['size'], enum_value, self.path))
                                return None
                            val = enum_value

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
                      .format(elementName, argument['type'], argument['name'], self.path))
                return None
        except TypeError:
            print("/!\\ Argument encoding for '{}' failed. "
                  "Unable to use '{}' as '{}' value as requested by argument '{}'"
                  .format(elementName, argument['value'], argument['type'], argument['name']))
            return None
        except ValueError:
            print("/!\\ Argument encoding for '{}' failed. "
                  "Unable to convert '{}' as '{}' value as requested by argument '{}'"
                  .format(elementName, argument['value'], argument['type'], argument['name']))
