import abc
from util import *


class CodeImpl(metaclass=abc.ABCMeta):
    def __init__(self):
        self.name = 'CodeImpl'

    # @todo booleanCheck variable used as flag for boolean verification should have a unique identifier to avoid
    # issue when conditions are nested. This one should be handled in the global CodeImpl class
    @staticmethod
    def boolean(codeImpl, boolean):
        if issubclass(type(codeImpl), CodeImpl):
            try:
                param = convertArgumentArrayToList(boolean['args'])
                return eval('codeImpl.' + boolean['name'] + '(' + param + ')')
            except Exception as e:
                print("Impossible to call boolean implementation.\nError: {}".format(e))

    @staticmethod
    def checkMotorsPorts(port):
        supported_values = ['A', 'B', 'C', 'D']
        if port in supported_values:
            return True
        return False

    @staticmethod
    def checkSensorsPorts(port):
        supported_values = ['1', '2', '3', '4']
        if port in supported_values:
            return True
        return False

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
    def c_end(self):
        pass

    @abc.abstractmethod
    def c_forever(self):
        pass

    @abc.abstractmethod
    def c_if(self, boolean):
        pass

    @abc.abstractmethod
    def c_repeat(self, times):
        pass

    @abc.abstractmethod
    def c_repeat_until(self, boolean):
        pass

    @abc.abstractmethod
    def c_else(self):
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
    def motors_run_direction(self, port, direction, unit, value):
        pass

    @abc.abstractmethod
    def motors_start_speed(self, port, direction, speed):
        pass

    @abc.abstractmethod
    def motors_stop(self, port):
        pass

    @abc.abstractmethod
    def set_status_light(self, color):
        pass

    @abc.abstractmethod
    def wait_seconds(self, seconds):
        pass

    @abc.abstractmethod
    def wait_touch(self, port, state):
        pass

    @abc.abstractmethod
    def wait_until(self, boolean):
        pass

    ###############################
    # BOOLEAN IMPLEMENTATIONS
    ###############################

    @abc.abstractmethod
    def b_touch(self, port):
        pass

    @abc.abstractmethod
    def b_distance(self, port, operator, value, unit):
        pass
