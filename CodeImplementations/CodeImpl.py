import abc
from util import *


class CodeImpl(metaclass=abc.ABCMeta):
    def __init__(self):
        self.name = 'CodeImpl'

    @staticmethod
    def boolean(codeImpl, boolean):
        if issubclass(type(codeImpl), CodeImpl):
            try:
                param = convertArgumentArrayToList(boolean['args'])
                return eval('codeImpl.' + boolean['name'] + '(' + param + ')')
            except Exception as e:
                print("Impossible to call boolean implementation.\nError: {}".format(e))

    ###############################
    # CodeImpl functions
    ###############################

    @abc.abstractmethod
    def getCode(self):
        pass

    @abc.abstractmethod
    def display(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def missingImplementationHandler(self, block, args):
        pass

    ###############################
    # C BLOCKS IMPLEMENTATIONS
    ###############################

    @abc.abstractmethod
    def c_forever(self):
        pass

    @abc.abstractmethod
    def c_if(self, boolean):
        pass

    @abc.abstractmethod
    def c_else(self):
        pass

    @abc.abstractmethod
    def c_end(self):
        pass

    ###############################
    # H BLOCKS IMPLEMENTATIONS
    ###############################

    @abc.abstractmethod
    def h_on_start(self):
        pass

    ###############################
    # STACK BLOCKS IMPLEMENTATIONS
    ###############################

    @abc.abstractmethod
    def wait_seconds(self, seconds):
        pass

    # @abc.abstractmethod
    # def wait_touch(self, port, state):
    #     pass

    @abc.abstractmethod
    def set_status_light(self, color):
        pass

    # @abc.abstractmethod
    # def motors_run_direction(self, port, direction, unit, value):
    #     pass

    # @abc.abstractmethod
    # def motors_start_speed(self, port, direction, value):
    #     pass

    # @abc.abstractmethod
    # def motors_stop(self, port):
    #     pass

    ###############################
    # BOOLEAN IMPLEMENTATIONS
    ###############################

    @abc.abstractmethod
    def b_touch(self, port):
        pass
