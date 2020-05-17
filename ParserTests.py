import unittest
from CommandType import CommandType
from Command import Command
from VMCController import VMCController
from Operand import OperandType

class ParserTests(unittest.TestCase):
    def test_all_command_types(self):
        self.assertEqual(CommandType.parse('mov'), CommandType.mov)
        self.assertEqual(CommandType.parse('store'), CommandType.store)
        self.assertEqual(CommandType.parse('neg'), CommandType.neg)
        self.assertEqual(CommandType.parse('add'), CommandType.add)
        self.assertEqual(CommandType.parse('sub'), CommandType.sub)
        self.assertEqual(CommandType.parse('less'), CommandType.less)
        self.assertEqual(CommandType.parse('eq'), CommandType.eq)
        self.assertEqual(CommandType.parse('logic_not'), CommandType.logic_not)
        self.assertEqual(CommandType.parse('logic_and'), CommandType.logic_and)
        self.assertEqual(CommandType.parse('logic_or'), CommandType.logic_or)
        self.assertEqual(CommandType.parse('binary_not'), CommandType.binary_not)
        self.assertEqual(CommandType.parse('push'), CommandType.push)
        self.assertEqual(CommandType.parse('pop'), CommandType.pop)
        self.assertEqual(CommandType.parse('ret'), CommandType.ret)
        self.assertEqual(CommandType.parse('jmp'), CommandType.jmp)
        self.assertEqual(CommandType.parse('label'), CommandType.label)
        self.assertEqual(CommandType.parse('jnz'), CommandType.jnz)
        self.assertEqual(CommandType.parse('call'), CommandType.call)
        self.assertEqual(CommandType.parse('read'), CommandType.read)
        self.assertEqual(CommandType.parse('write'), CommandType.write)

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

if __name__ == '__main__':
    unittest.main()
