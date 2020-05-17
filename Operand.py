from enum import Enum


class OperandType(Enum):
    immediate = 0
    register = 1
    label = 2


class Operand:
    """
    An operand in an ASM command
    """

    @classmethod
    def resolve_immediate(cls, immediate_string):
        """
        Resolve an immediate, Return None if it's not a valid immediate
        TODO: add support for hex and const expressions
        """
        if immediate_string == 'True':
            return 1
        elif immediate_string == 'False':
            return 0
        try:
            return int(immediate_string)
        except ValueError:
            return None

    @classmethod
    def resolve_register(cls, register_name, register_list):
        """
        Return the offset of a register, or None if no such public register exists
        """
        try:
            return register_list.get_register_offset(register_name, True)
        except ValueError:
            return None

    def __init__(self, text, register_list):
        if Operand.resolve_immediate(text) is not None:
            self.type = OperandType.immediate
            self.value = Operand.resolve_immediate(text)
        elif Operand.resolve_register(text, register_list) is not None:
            self.type = OperandType.register
            self.value = Operand.resolve_register(text, register_list)
        else:
            self.type = OperandType.label
            self.value = text

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value
