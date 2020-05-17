from CommandType import CommandType
from Operand import Operand


class Command:
    """
    A single ASM command and it's operands
    """

    def __init__(self, command_text):
        """
        Parses a command.
        The command should be without leading or trailing whitespaces, and without comments
        Raises ValueError if the command is invalid
        """
        command_parts = command_text.split()
        self.command_type = CommandType(command_parts[0])
        self.operands = [Operand(operand) for operand in command_parts[1:]]
