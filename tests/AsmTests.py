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

    def test_add_two_immediates(self):
        code = """4 256 14 5 True
                  add r0 999 -99"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 900)

    def test_add_immediate_register(self):
        code = """4 256 14 5 True
                  mov r1 1
                  add r0 999 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1000)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_add_register_register(self):
        code = """4 256 14 5 True
                  mov r1 1
                  mov r2 3
                  add r0 r2 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 4)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 3)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_add_3_times_same_register(self):
        code = """4 256 14 5 True
                  mov r0 5
                  add r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 10)

    def test_increment_register_left(self):
        code = """4 256 14 5 True
                  mov r0 5
                  add r0 7 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 12)

    def test_increment_register_right(self):
        code = """4 256 14 5 True
                  mov r0 5
                  add r0 r0 7"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 12)

    def test_increment_register_with_register(self):
        code = """4 256 14 5 True
                  mov r0 5
                  mov r2 12340
                  add r0 r0 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 12345)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 12340)


if __name__ == '__main__':
    unittest.main()
