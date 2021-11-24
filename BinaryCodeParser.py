import xml.etree.ElementTree as ET


class BinaryCodeParser:
    def __init__(self, path):
        self.path = path

        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()

        info = self.root.find("info")

        self.version = float(info.find("version").text)
        self.idSize = int(info.find("blockIdSize").text)

        print("Schema {} loaded for V{}, block id size is {}".format(self.path, self.version, self.idSize))

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

        print("Binary successfully decoded")

        return code

    def findNextFunction(self, requestId, binaryCode):
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

        blocks = self.root.find("blocks")

        for block in blocks:
            if block.attrib['name'] == requestBlock:

                id_hex = block.find("id").text
                id_int = int(id_hex, 16)
                id_bin = bin(id_int)[2:].zfill(self.idSize)

                args = block.find("arguments")

                ret_args = []
                args_length = 0

                if args:
                    for arg in args:
                        arg_name = arg.tag
                        arg_size = int(arg.attrib['size'])
                        arg_type = arg.attrib['type']
                        arg_value = argsList[arg_name]

                        args_length += arg_size

                        if arg_type == 'uint':
                            val = bin(arg_value)[2:].zfill(arg_size)
                            ret_args.append(val)
                        else:
                            print("/!\\ Unknown argument type")

                padding_size = self.calculatePaddingSize(args_length)
                padding = '' + '0' * padding_size

                ret = id_bin + ''.join(ret_args) + padding

                print("{} found: id={} ({}), args={}, padding={} bits. Code: {}".
                      format(requestBlock, id_hex, id_int, ret_args, padding_size, hex(int(ret, 2))))

                return ret

        # If requested block was not found
        return None
