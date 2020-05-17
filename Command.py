from CommandType import CommandType
from Operand import Operand


class Command:
    """
    A single ASM command and it's operands
    """

    def __init__(self, command_text, register_list, basic_block_idx):
        """
        Parses a command.
        The command should be without leading or trailing whitespaces, and without comments
        Raises ValueError if the command is invalid
        """
        command_parts = command_text.split()
        self.command_type = CommandType.parse(command_parts[0])
        self.operands = [Operand(operand, register_list) for operand in command_parts[1:]]
        self.basic_block_idx = basic_block_idx

    def compile(self, controller, label_to_basic_block):
        raise NotImplementedError()

