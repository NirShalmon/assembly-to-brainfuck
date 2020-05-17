import unittest
from CommandType import CommandType


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


if __name__ == '__main__':
    unittest.main()
