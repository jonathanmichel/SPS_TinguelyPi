"""
Author: Jonathan Michel
Date:   26.01.2022
This class decodes a string that represents the frame received from the Arduino blocks.
This frame represents a Scratch program with each block having a unique id and a  pre-defined list of parameters.
The protocol is specified in an XML file that has to be passed to the constructor, see the documentation for
additional information.
"""
import xml.etree.ElementTree as ET


class FrameDecoder:
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

                print("Schema {} loaded for V{}, block id size is {} chars (max value 0x{})".
                      format(self.path, self.version, self.idSize, 'F' * self.idSize))
            except:
                print("Invalid xml, specify version and idSize tags in <info>: {}".format(self.path))

        else:
            print("Invalid xml, specify info tag in {}".format(self.path))

    def parseFrame(self, frame):
        if not self.validXml:
            print("Unable to parse frame, invalid xml")
            return None

        if frame:
            print("Converting frame: {}".format(frame))
        else:
            print("Unable to parse frame, it is empty")
            return None

        code = []

        while frame:
            # Extract blocks and its arguments
            (frame, block) = self.decodeBlock(frame)

            if block:
                code.append(block)
            else:
                print("Error parsing frame. {} line(s) decoded before error".format(len(code)))
                return None

        print("Successfully converted frame in {} line(s) of code".format(len(code)))

        return code

    # Elements can be "blocks" or "booleans"
    def decode(self, rootElement, frame):
        if not self.validXml:
            print("Decoding failed, invalid xml")
            return None, None

        if len(frame) < self.idSize:
            print("Decoding failed, remaining frame '{}' has not enough data".format(frame))
            return None, None

        element_id_hex = frame[0:self.idSize]
        # Get element id in frame
        try:
            element_id = int(str(element_id_hex), 16)
        except ValueError:  # invalid id extracted
            print("Decode frame fails, invalid id '{}'".format(element_id_hex))
            return None, None

        # print("Trying to decode '{}' {} in {}".format(rootElement, hex(element_id), frame))

        # Remove hex id from frame
        frame = frame[self.idSize:]

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

                (ret_args, frame) = self.decodeArguments(args, frame)

                if ret_args is not None:
                    # Construction element object to return
                    ret = {
                        'id': id,
                        'name': element.attrib['name'],
                        'args': ret_args
                    }

                    # print("\Element found in {}: {}".format(rootElement, ret))

                    return frame, ret
                else:   # Unable to decode argument
                    break

        print("Abort decoding for {}".format(hex(element_id)))

        # If element was not found
        return None, None

    def decodeBlock(self, binaryCode):
        return self.decode("blocks", binaryCode)

    def decodeBoolean(self, binaryCode):
        return self.decode("booleans", binaryCode)

    def decodeArguments(self, arguments, frame):
        ret_args = []
        args_length = 0

        # print("Decode argument for {} in {}".format(arguments, frame))

        if arguments:
            for arg in arguments:
                arg_type = arg.attrib['type']

                # if argument is a binary chain (used for boolean), the size (in hex) is
                # defined by the next char, otherwise argument size (in chars) is specified in xml definition
                if arg_type == 'binary':
                    arg_size = int(frame[0:1], 16)
                    frame = frame[1:]
                else:
                    arg_size = int(arg.attrib['size'])

                # Get argument value and convert it according to its type
                arg_value = frame[0:arg_size]

                arg_value = self.decodeArgumentValue(arg_type, arg_value, arg)

                if arg_value is not None:
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

                    # Remove current argument from local frame
                    frame = frame[arg_size:]
                else:
                    return None, None

        # @todo remove next '|'
        if len(frame):
            if frame[0] == '|':
                frame = frame[1:]
            else:
                print("Invalid frame, separator waited here: '{}'".format(frame))
                return None, None

        # If there is no argument
        return ret_args, frame

    def decodeArgumentValue(self, argType, argValue, argumentsXml):
        arg_value = None
        try:
            if argType == 'uint':  # Convert string representation value to int
                arg_value = int(argValue)
            elif argType == 'enum':  # Convert string representation value to enum
                arg_value = 'N/A'  # Default str if enum value is invalid
                for enum in argumentsXml:
                    # Check if value is available in enum
                    if argValue == enum.attrib['value']:
                        arg_value = enum.text
                        break

                if arg_value == 'N/A':
                    print("/!\\ Decoding failed, unable to convert value '{}' for enum '{}'"
                          .format(argValue, argumentsXml.tag))
                    return None

            elif argType == 'binary':  # Convert binary value to boolean or reporter
                (_, arg_value) = self.decodeBoolean(argValue)
                # We do not use frame returned by decodeBoolean() because chars are
                # already removed from frame by the current block
        except ValueError as ve:  # Unable to convert value
            print("/!\\ Decoding failed, unable to convert '{}' as type '{}'"
                  .format(argValue, argType))
            return None

        return arg_value
