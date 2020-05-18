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

    def test_store_immediate_at_immediate(self):
        code = """4 256 14 5 True
                  store 2 123456789"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_memory(2), 123456789)

    def test_store_immediate_at_register(self):
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

    def test_load_immediate_at_register(self):
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

    def test_increment_register_with_register_right(self):
        code = """4 256 14 5 True
                  mov r0 5
                  mov r2 12340
                  add r0 r2 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 12345)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 12340)

    def test_add_same_register_twice(self):
        code = """4 256 14 5 True
                  mov r0 5
                  mov r2 12340
                  add r0 r2 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 12340*2)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 12340)

    def test_sub_two_immediates(self):
        code = """4 256 14 5 True
                  sub r0 999 998"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_sub_immediate_register(self):
        code = """4 256 14 5 True
                  mov r1 1
                  mov r0 12345
                  sub r0 999 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 998)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_sub_register_register(self):
        code = """4 256 14 5 True
                  mov r1 1
                  mov r2 3
                  sub r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), -2)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 3)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_sub_3_times_same_register(self):
        code = """4 256 14 5 True
                  mov r0 5
                  sub r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_sub_immediate_left(self):
        code = """4 256 14 5 True
                  mov r0 5
                  sub r0 7 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 2)

    def test_decrement_register_right(self):
        code = """4 256 14 5 True
                  mov r0 5
                  sub r0 r0 7"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), -2)

    def test_decrement_register_with_register(self):
        code = """4 256 14 5 True
                  mov r0 5
                  mov r2 2
                  sub r0 r0 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 3)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 2)

    def test_sub_same_register_twice(self):
        code = """4 256 14 5 True
                  mov r0 5
                  mov r2 12340
                  sub r0 r2 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 12340)

    def test_less_immediates_true(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  less r0 5 10"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_less_immediates_false(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  less r0 789 10"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_less_registers_true(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 17
                  mov r2 99
                  less r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 17)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 99)

    def test_less_registers_false(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 17
                  mov r2 99
                  less r0 r2 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 17)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 99)

    def test_less_register_self(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  less r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_less_register_self_and_other_true(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 1
                  less r0 r1 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_less_register_self_and_other_false(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 1
                  less r0 r0 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_eq_immediates_true(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  eq r0 5 5"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_eq_immediates_false(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  eq r0 789 10"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_eq_registers_true(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 257
                  mov r2 257
                  eq r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 257)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 257)

    def test_eq_registers_false(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 17
                  mov r2 99
                  eq r0 r2 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 17)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 99)

    def test_eq_register_self(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  eq r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_eq_register_self_and_other_false(self):
        code = """4 256 14 5 True
                  mov r0 123456789
                  mov r1 1
                  eq r0 r1 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_eq_register_self_and_other_true(self):
        code = """4 256 14 5 True
                  mov r0 1
                  mov r1 1
                  eq r0 r1 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_logic_not_false(self):
        code = """4 256 14 5 True
                  mov r0 False
                  logic_not r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_logic_not_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  logic_not r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_logic_and_self_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  logic_and r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_logic_and_self_false(self):
        code = """4 256 14 5 True
                  mov r0 False
                  logic_and r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_logic_and_with_two_equal_true(self):
        code = """4 256 14 5 True
                  mov r0 False
                  mov r1 True
                  logic_and r0 r1 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_logic_and_with_two_equal_false(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r1 False
                  logic_and r0 r1 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)

    def test_logic_and_with_two_other_false(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r2 True
                  mov r1 False
                  logic_and r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 1)

    def test_logic_and_with_two_other_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r2 True
                  mov r1 True
                  logic_and r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 1)

    def test_logic_and_self_with_other_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r1 True
                  logic_and r0 r0 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_logic_and_self_with_other_false(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r1 False
                  logic_and r0 r0 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)

    def test_logic_or_self_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  logic_or r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)

    def test_logic_or_self_false(self):
        code = """4 256 14 5 True
                  mov r0 False
                  logic_or r0 r0 r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)

    def test_logic_or_with_two_equal_true(self):
        code = """4 256 14 5 True
                  mov r0 False
                  mov r1 True
                  logic_or r0 r1 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)

    def test_logic_or_with_two_equal_false(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r1 False
                  logic_or r0 r1 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)

    def test_logic_or_with_two_other_false(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r2 False
                  mov r1 False
                  logic_or r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 0)

    def test_logic_or_with_two_other_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r2 False
                  mov r1 True
                  logic_or r0 r1 r2"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 0)

    def test_logic_or_self_with_other_true(self):
        code = """4 256 14 5 True
                  mov r0 True
                  mov r1 False
                  logic_or r0 r0 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)

    def test_logic_or_self_with_other_false(self):
        code = """4 256 14 5 True
                  mov r0 False
                  mov r1 False
                  logic_or r0 r0 r1"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), 0)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 0)

    def test_binary_not_zero(self):
        code = """4 256 14 5 True
                     mov r0 0
                     binary_not r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), -1)

    def test_binary_not_long(self):
        code = """4 256 14 5 True
                     mov r0 123456789
                     binary_not r0"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), -123456789-1)

    def test_push_pop(self):
        code = """4 256 14 5 True
                    push 1234
                    push -1
                    mov r0 17
                    push r0
                    pop r1
                    mov r0 3
                    push r0
                    pop r2
                    pop r0
                    pop r3"""
        controller = VMCController(4, 256, 14, 5)
        debugger = Debugger(controller, compile_code(code))
        debugger.exec_commands(10000000)
        self.assertTrue(debugger.execution_completed)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[1], as_signed_num=True), 17)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[2], as_signed_num=True), 3)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[0], as_signed_num=True), -1)
        self.assertEqual(debugger.get_vmc_value(controller.offset_reg[3], as_signed_num=True), 1234)



if __name__ == '__main__':
    unittest.main()
