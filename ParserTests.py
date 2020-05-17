import unittest
from CommandType import CommandType
from Command import Command
from VMCController import VMCController
from Operand import OperandType
from compiler import parse_code


class ParserTests(unittest.TestCase):
    def test_all_command_types(self):
        self.assertEqual(CommandType['mov'], CommandType.mov)
        self.assertEqual(CommandType['store'], CommandType.store)
        self.assertEqual(CommandType['neg'], CommandType.neg)
        self.assertEqual(CommandType['add'], CommandType.add)
        self.assertEqual(CommandType['sub'], CommandType.sub)
        self.assertEqual(CommandType['less'], CommandType.less)
        self.assertEqual(CommandType['eq'], CommandType.eq)
        self.assertEqual(CommandType['logic_not'], CommandType.logic_not)
        self.assertEqual(CommandType['logic_and'], CommandType.logic_and)
        self.assertEqual(CommandType['logic_or'], CommandType.logic_or)
        self.assertEqual(CommandType['binary_not'], CommandType.binary_not)
        self.assertEqual(CommandType['push'], CommandType.push)
        self.assertEqual(CommandType['pop'], CommandType.pop)
        self.assertEqual(CommandType['ret'], CommandType.ret)
        self.assertEqual(CommandType['jmp'], CommandType.jmp)
        self.assertEqual(CommandType['label'], CommandType.label)
        self.assertEqual(CommandType['jnz'], CommandType.jnz)
        self.assertEqual(CommandType['call'], CommandType.call)
        self.assertEqual(CommandType['read'], CommandType.read)
        self.assertEqual(CommandType['write'], CommandType.write)

    def test_command_parsing(self):
        controller = VMCController(4, 256, 14, 5)
        command = Command("mov r0 r4 1789 fasfa True False", controller.register_list, 0)
        self.assertEqual(command.command_type, CommandType.mov)
        self.assertEqual(command.operands[0].type, OperandType.register)
        self.assertEqual(command.operands[0].value, controller.register_list.get_register_offset("r0"))
        self.assertEqual(command.operands[1].type, OperandType.register)
        self.assertEqual(command.operands[1].value, controller.register_list.get_register_offset("r4"))
        self.assertEqual(command.operands[2].type, OperandType.immediate)
        self.assertEqual(command.operands[2].value, 1789)
        self.assertEqual(command.operands[3].type, OperandType.label)
        self.assertEqual(command.operands[3].value, 'fasfa')
        self.assertEqual(command.operands[4].type, OperandType.immediate)
        self.assertEqual(command.operands[4].value, 1)
        self.assertEqual(command.operands[5].type, OperandType.immediate)
        self.assertEqual(command.operands[5].value, 0)

    def test_parse_private_register(self):
        controller = VMCController(4, 256, 14, 5)
        command = Command("mov r0 r_heap_value", controller.register_list, 0)
        self.assertEqual(command.operands[1].type, OperandType.label)

    def test_code_parser(self):
        source = """   #Comment  fasf 
                    4 256 14 5 #vmc variables
                    mov r0 1234
                    jmp target
                    label target
                    push True
                    label end"""
        controller, commands, label_to_basic_block = parse_code(source)
        self.assertEqual(controller.num_size, 4)
        self.assertEqual(controller.cell_range, 256)
        self.assertEqual(len(controller.offset_temp), 14)
        self.assertEqual(len(controller.offset_reg), 5)
        self.assertEqual(len(commands), 5)
        self.assertEqual(commands[1].operands[0].value, 'target')
        self.assertEqual(commands[3].operands[0].value, 1)
        self.assertEqual(commands[1].basic_block_idx, 0)
        self.assertEqual(commands[4].basic_block_idx, 2)
        self.assertEqual(label_to_basic_block['target'], 2)
        self.assertEqual(label_to_basic_block['end'], 3)


if __name__ == '__main__':
    unittest.main()
