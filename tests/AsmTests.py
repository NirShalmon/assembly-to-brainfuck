import unittest
from compiler import compile_code
from Debugger import Debugger
from VMCController import VMCController


class AsmTests(unittest.TestCase):

    def test_mov_immediate(self):
        code = """4 256 14 5
                  mov r0 123456"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0]), 123456)

    def test_mov_register(self):
        code = """4 256 14 5
                  mov r0 123456789
                  mov r1 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(100000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1]), 123456789)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0]), 123456789)

    def test_mov_register_to_self(self):
        code = """4 256 14 5
                  mov r0 -1
                  mov r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(100000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0]),
                         controller.cell_range ** controller.num_size - 1)

    def test_store_immidiate_at_immidiate(self):
        code = """4 256 14 5 True
                  store 2 123456789"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_memory(2), 123456789)

    def test_store_immidiate_at_register(self):
        code = """4 256 14 5 True
                  mov r0 2
                  store r0 -123"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_memory(2, as_signed_num=True), -123)

    def test_store_register_at_register(self):
        code = """4 256 14 5 True
                  mov r0 2
                  mov r1 -9999
                  store r0 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_memory(2, as_signed_num=True), -9999)

    def test_load_register_at_register(self):
        code = """4 256 14 5 True
                  mov r0 2
                  mov r1 -9999
                  store r0 r1
                  load r2 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_memory(2, as_signed_num=True), -9999)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), -9999)

    def test_load_immidiate_at_register(self):
        code = """4 256 14 5 True
                  mov r0 2
                  mov r1 -9999
                  store r0 r1
                  load r2 2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_memory(2, as_signed_num=True), -9999)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), -9999)

    def test_negate_negative_register(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  neg r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), -123456789)


if __name__ == '__main__':
    unittest.main()
