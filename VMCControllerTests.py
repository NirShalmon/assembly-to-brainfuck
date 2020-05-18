import unittest
import VMCController
from Debugger import Debugger


class TestVMCController(unittest.TestCase):

    def setUp(self):
        self.controller = VMCController.VMCController(4, 256, 14, 5)

    def test_set_copy(self):
        test_code = self.controller.set_num(4, 54321) \
                    + self.controller.set_num(0, 12345) \
                    + self.controller.set_num(8, -1) \
                    + self.controller.copy_num(0, 4)
        debugger = Debugger(self.controller, test_code)
        debugger.exec_commands(100000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value_unsigned(0), 12345)
        self.assertEqual(debugger.get_vmc_value_unsigned(4), 12345)
        self.assertEqual(debugger.get_vmc_value_unsigned(8), self.controller.cell_range ** self.controller.num_size - 1)

    def test_if_else_true(self):
        test_code = []
        test_code.append(self.controller.set_byte(0, 12))
        if_code, temps = self.controller.if_else_byte_if(0)
        test_code.append(if_code)
        test_code.append(self.controller.set_num(2, 12345))
        if_code, temps = self.controller.if_else_byte_else(0, temps)
        test_code.append(if_code)
        test_code.append(self.controller.set_num(2, 54321))
        test_code.append(self.controller.if_else_byte_end(0, temps))
        debugger = Debugger(self.controller, ''.join(test_code))
        debugger.exec_commands(100000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value_unsigned(2), 12345)

    def test_if_else_false(self):
        test_code = []
        test_code.append(self.controller.set_byte(0, 0))
        if_code, temps = self.controller.if_else_byte_if(0)
        test_code.append(if_code)
        test_code.append(self.controller.set_num(8, 12345))
        if_code, temps = self.controller.if_else_byte_else(0, temps)
        test_code.append(if_code)
        test_code.append(self.controller.set_num(4, 54321))
        test_code.append(self.controller.if_else_byte_end(0, temps))
        debugger = Debugger(self.controller, ''.join(test_code))
        debugger.exec_commands(100000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value_unsigned(4), 54321)
        self.assertEqual(debugger.get_vmc_value_unsigned(8), 0)

    def test_decrement(self):
        code = [self.controller.set_num(0, 1),
                self.controller.increment_num(0, -1)]
        debugger = Debugger(self.controller, ''.join(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value_unsigned(0), 0)

    def test_store(self):
        code = [self.controller.set_num(self.controller.offset_reg[0], 6)]
        code += [self.controller.set_byte(self.controller.offset_reg[2], 1)]
        code += [self.controller.while_byte_start(self.controller.offset_reg[2])]
        code += [self.controller.store_memory(self.controller.offset_reg[1], self.controller.offset_reg[1])]
        code += [self.controller.increment_num(self.controller.offset_reg[1], 2)]
        code += [self.controller.equal_num(self.controller.offset_reg[1], self.controller.offset_reg[0],
                                           self.controller.offset_reg[2])]
        code += [self.controller.increment_byte(self.controller.offset_reg[2], -1)]
        code += [self.controller.while_byte_end(self.controller.offset_reg[2])]
        code += [self.controller.set_num(self.controller.offset_reg[0], 1)]
        code += [self.controller.set_byte(self.controller.offset_reg[2], 1)]
        code += [self.controller.increment_num(self.controller.offset_reg[1], -1)]
        code += [self.controller.while_byte_start(self.controller.offset_reg[2])]
        code += [self.controller.store_memory(self.controller.offset_reg[1], self.controller.offset_reg[1])]
        code += [self.controller.increment_num(self.controller.offset_reg[1], -2)]
        code += [self.controller.equal_num(self.controller.offset_reg[1], self.controller.offset_reg[0],
                                           self.controller.offset_reg[2])]
        code += [self.controller.increment_byte(self.controller.offset_reg[2], -1)]
        code += [self.controller.while_byte_end(self.controller.offset_reg[2])]
        debugger = Debugger(self.controller, ''.join(code))
        debugger.exec_commands(100000000)
        self.assertTrue(debugger.execution_completed)
        for i in range(0, 6, 2):
            self.assertEqual(debugger.get_memory_unsigned(i), i)
        self.assertEqual(debugger.get_memory_unsigned(6), 0)
        self.assertEqual(debugger.get_memory_unsigned(1), 0)
        for i in range(5, 1, -2):
            self.assertEqual(debugger.get_memory_unsigned(i), i)

    def test_sequential_basic_blocks(self):
        code = [self.controller.opening_code(),
                self.controller.basic_block_start(),
                self.controller.set_num(self.controller.offset_reg[0], 12345),
                self.controller.basic_block_goto_next(),
                self.controller.basic_block_start(),
                self.controller.set_num(self.controller.offset_reg[1], 54321),
                self.controller.basic_block_goto_next(),
                self.controller.closing_code()]
        debugger = Debugger(self.controller, ''.join(code))
        debugger.exec_commands(100000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value_unsigned(self.controller.offset_reg[0]), 12345)
        self.assertEqual(debugger.get_vmc_value_unsigned(self.controller.offset_reg[1]), 54321)


if __name__ == '__main__':
    unittest.main()
