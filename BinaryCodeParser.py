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

    def parse(self, binary):
        print("Decoding binary...")

        code = []

        while binary:
            # Get functionId and remove it from binary chain
            function_id = binary[0:self.idSize]
            binary = binary[self.idSize:]
            # Extract function and its arguments
            function_res = self.findNextFunction(int(function_id), binary)
            arg_length = int(function_res['args_length'])

            # Remove arguments binary data from binary chain
            binary = binary[arg_length:]
            code.append(function_res)

            # print(function_res)

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

                # Get arguments  required by found function
                args_length = 0
                args = block.find("arguments")

                if args:
                    for arg in args:
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
                id_bin = bin(id_int)[2:].zfill(7)

                args = block.find("arguments")

                ret_args = []

                if args:
                    for arg in args:
                        arg_name = arg.tag
                        arg_size = int(arg.attrib['size'])
                        arg_type = arg.attrib['type']
                        arg_value = argsList[arg_name]

                        if arg_type == 'uint':
                            val = bin(arg_value)[2:].zfill(arg_size)
                            ret_args.append(val)
                        else:
                            print("/!\\ Unknown argument type")

                # print("{} found: id={} ({}), args={}".format(requestBlock, id_hex, id_int, ret_args))

                return id_bin + ''.join(ret_args)

        # If requested block was not found
        return None
