import sys
from VMCController import VMCController
from Debugger import Debugger
from Command import Command
from CommandType import CommandType
from Operand import OperandType


def parse_vmc_definition(vmc_definition):
    """
    Parses the VMC definition at the start of the code file
    """
    is_debug = len(vmc_definition.split()) == 5 and vmc_definition.split()[-1] == 'True'
    num_size, cell_range, temp_amount, register_amount = [int(num) for num in vmc_definition.split()[:4]]
    return VMCController(num_size, cell_range, temp_amount, register_amount, is_debug)


def parse_code(source):
    """
    Returns the VMCController, a list of Command objects, and a label_to_basic_block dictionary
    """
    source_lines = [line.strip() for line in source.splitlines()]
    commands_text = [(line[:line.find('#')] if '#' in line else line).rstrip() for line in source_lines if
                     len(line) > 0 and line[0] != '#']
    controller = parse_vmc_definition(commands_text[0])
    commands = []
    label_to_basic_block = {'start': 0}
    basic_block_idx = 0
    for command_text in commands_text[1:]:
        command = Command(command_text, controller.register_list, basic_block_idx)
        if command.command_type == CommandType.label:
            label_to_basic_block[command.operands[0].value] = basic_block_idx + 1  # Label points to next basic block
        if command.command_type.ends_basic_block():
            basic_block_idx += 1
        commands.append(command)
    if not commands[-1].command_type.ends_basic_block():
        basic_block_idx += 1
    label_to_basic_block['exit'] = basic_block_idx
    return controller, commands, label_to_basic_block


def compile_code(source):
    """
    Returns the compiled brainfuck of source
    """
    controller, commands, label_to_basic_block = parse_code(source)
    if len(commands) == 0:
        return ''
    output = [controller.opening_code(), controller.basic_block_start()]
    for command_idx, command in enumerate(commands):
        output.append(command.compile(controller, label_to_basic_block))
        if command_idx != len(commands) - 1 and command.command_type.ends_basic_block():
            output.append(controller.basic_block_start())
    if not commands[-1].command_type.ends_basic_block():
        output.append(controller.basic_block_goto_next())
    output.append(controller.closing_code())
    return ''.join(output)


def compile_file(source_file, output_file):
    with open(source_file, 'r') as f_source:
        source = f_source.read()
    with open(output_file, 'w') as f_out:
        f_out.write(compile_code(source))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage {sys.argv[0]} code_file output_file')
    compile_file(sys.argv[1], sys.argv[2])
