from VMCController import VMCController
from Debugger import Debugger
from Command import Command
from CommandType import CommandType
from Operand import OperandType


def parse_vmc_definition(vmc_definition):
    """
    Parses the VMC definition at the start of the code file
    """
    num_size, cell_range, temp_amount, register_amount = [int(num) for num in vmc_definition.split()]
    return VMCController(num_size, cell_range, temp_amount, register_amount)


def parse_code(source):
    """
    Returns the VMCController, a list of Command objects, and a label_to_basic_block dictionary
    """
    source_lines = [line.strip() for line in source.splitlines()]
    commands_text = [(line[:line.find('#')] if '#' in line else line).rstrip() for line in source_lines if len(line) > 0 and line[0] != '#']
    controller = parse_vmc_definition(commands_text[0])
    commands = []
    label_to_basic_block = dict()
    basic_block_idx = 0
    for command_text in commands_text[1:]:
        command = Command(command_text, controller.register_list, basic_block_idx)
        if command.command_type == CommandType.label:
            label_to_basic_block[command.operands[0].value] = basic_block_idx + 1  # Label points to next basic block
        if command.command_type.ends_basic_block():
            basic_block_idx += 1
        commands.append(command)
    return controller, commands, label_to_basic_block


'''
def compile(source):
    """
    Returns the compiled brainfuck of source
    """
    controller, commands, label_to_basic_block = parse_code(source)
    if len(commands) == 0:
        return ''
    output = [controller.opening_code()]
    for command in commands:
        output.append(command.compile(controller, label_to_basic_block))
    if not commands[-1].command_type.ends_basic_block():
        output.append(controller.basic_block_goto_next())
    output.append(controller.closing_code())
    return ''.join(output)
'''