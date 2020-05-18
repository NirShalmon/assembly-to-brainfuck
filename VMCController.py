from TempAllocator import TempAllocator
from Register import Register, RegisterList


class VMCController:
    """
    num_size is the number of bytes per number
    cell_range is one plus the max number in each byte. i.e 256
    """

    def __init__(self, num_size, cell_range, temp_amount, register_amount, debug=False):
        register_list = [Register('r_heap_value', False, False, num_size),
                         Register('r_stack_value', False, False, num_size),
                         Register('r_cell_index', False, False, num_size),
                         Register('r_target_cell', True, False, num_size),  # This register is not strictly necessary
                         Register('r_cur_cmd', False, False, num_size),
                         Register('r_stack_pointer', True, False, num_size),
                         Register('r_flow_reserved', False, False, num_size)]
        register_list += [Register(f'r{i}', True, True, num_size) for i in range(register_amount)]
        register_list += [Register(f't{i}', False, False, num_size) for i in range(temp_amount)]
        self.register_list = RegisterList(register_list)
        self.vmc_size = self.register_list.total_size()
        self.cur_offset = 0
        self.num_size = num_size
        self.cell_range = cell_range
        self.offset_heap_value = self.register_list.get_register_offset('r_heap_value')
        self.offset_stack_value = self.register_list.get_register_offset('r_stack_value')
        self.offset_cell_index = self.register_list.get_register_offset('r_cell_index')
        self.offset_target_cell = self.register_list.get_register_offset('r_target_cell')
        self.offset_cur_cmd = self.register_list.get_register_offset('r_cur_cmd')
        self.offset_stack_pointer = self.register_list.get_register_offset('r_stack_pointer')
        self.offset_flow_reserved = self.register_list.get_register_offset('r_flow_reserved')
        self.offset_reg = [self.register_list.get_register_offset(f'r{i}') for i in range(register_amount)]
        self.offset_temp = [self.register_list.get_register_offset(f't{i}') for i in range(temp_amount)]
        self.temp_allocator = TempAllocator(self.vmc_size, self.offset_temp)
        self.debug = debug

    def move_to_offset(self, offset):
        if self.cur_offset < offset:
            code = '>' * (offset - self.cur_offset)
        else:
            code = '<' * (self.cur_offset - offset)
        self.cur_offset = offset
        return code

    def while_byte_start(self, byte_offset):
        """
        while(byte_offset){
        """
        return self.move_to_offset(byte_offset) + '['

    def while_byte_end(self, byte_offset):
        return self.move_to_offset(byte_offset) + ']'

    def increment_byte(self, byte_offset, delta=1):
        if delta == 0:
            return ''
        return self.move_to_offset(byte_offset) + ('+' * delta if delta > 0 else '-' * (-delta))

    def print_byte_ascii(self, byte_offset):
        return self.move_to_offset(byte_offset) + '.'

    def input_byte_ascii(self, byte_offset):
        return self.move_to_offset(byte_offset) + ','

    def move_byte(self, from_offset, *to_offsets):
        """
        Zeros the byte at from_offset
        """
        code_parts = [self.clear_byte(to_offset) for to_offset in to_offsets]
        code_parts.append(self.while_byte_start(from_offset))
        code_parts.append(self.increment_byte(from_offset, -1))
        for to_offset in to_offsets:
            code_parts.append(self.increment_byte(to_offset, 1))
        code_parts.append(self.while_byte_end(from_offset))
        return ''.join(code_parts)

    def move_num(self, from_offset, *to_offsets):
        """
        Zeros the byte at from_offset
        """
        return ''.join(self.move_byte(from_offset + i, *(x + i for x in to_offsets)) for i in range(self.num_size))

    def copy_byte(self, from_offset, *to_offsets):
        temp = self.temp_allocator.alloc_temp()
        code = self.move_byte(from_offset, *(tuple([temp]) + to_offsets)) \
               + self.move_byte(temp, from_offset)
        self.temp_allocator.free(temp)
        return code

    def copy_num(self, from_offset, *to_offsets):
        return ''.join(
            self.copy_byte(from_offset + i, *(offset + i for offset in to_offsets)) for i in range(self.num_size)
        )

    def move_k_vmc(self, k):
        """
        Move to the VMC k vmcs to the right if k > 0
        Else move to the VMC -k vmcs to the left
        clears temp allocations
        """
        if k == 0:
            return ''
        # clear temp allocations
        target_vmc_offset = self.vmc_size * k
        # Copy global data
        code_parts = []
        for reg in self.register_list.get_preserved_offsets():
            code_parts.append(self.move_num(reg, reg + target_vmc_offset))
        # Update cell index, if k>0
        for vmc in range(0, k):
            code_parts.append(self.copy_num(self.offset_cell_index, self.vmc_size + self.offset_cell_index))
            self.cur_offset -= self.vmc_size
            if self.debug:
                code_parts.append("{" + f'move_vmc {1}' + "}")
            code_parts.append(self.increment_num(self.offset_cell_index, 1))
        if k < 0:
            if self.debug:
                code_parts.append("{" + f'move_vmc {k}' + "}")
            self.cur_offset -= target_vmc_offset
        return ''.join(code_parts)

    def clear_byte(self, cell_offset):
        return self.while_byte_start(cell_offset) \
               + self.increment_byte(cell_offset, -1) \
               + self.while_byte_end(cell_offset)

    def clear_num(self, cell_offset):
        return ''.join(self.clear_byte(cell_offset + i) for i in range(self.num_size))

    def set_byte(self, cell_offset, value):
        if value <= self.cell_range // 2:
            return self.clear_byte(cell_offset) + self.increment_byte(cell_offset, value)
        return self.clear_byte(cell_offset) + self.increment_byte(cell_offset, value - self.cell_range)

    def set_num(self, cell_offset, value):
        if value < 0:
            value = self.cell_range ** self.num_size + value
        code = [self.set_byte(cell_offset + i,
                              (abs(value) // (self.cell_range ** (self.num_size - i - 1))) % self.cell_range)
                for i in range(self.num_size)]
        return ''.join(code)

    def if_byte_if(self, cell_offset):
        temp = self.temp_allocator.alloc_temp()
        code = self.copy_byte(cell_offset, temp) + self.while_byte_start(temp)
        return code, temp

    def if_byte_end(self, cell_offset, temp):
        code = ''.join([
            self.clear_byte(temp),
            self.while_byte_end(temp)
        ])
        self.temp_allocator.free(temp)
        return code

    def if_else_byte_if(self, cell_offset):
        temps = self.temp_allocator.alloc_temps(2)
        code = ''.join([
            self.clear_byte(temps[1]),
            self.set_byte(temps[0], 1),
            self.while_byte_start(cell_offset)
        ])
        return code, temps

    def if_else_byte_else(self, cell_offset, temps):
        code = ''.join([
            self.increment_byte(temps[0], -1),
            self.move_byte(cell_offset, temps[1]),
            self.while_byte_end(cell_offset),
            self.move_byte(temps[1], cell_offset),
            self.while_byte_start(temps[0])
        ])
        self.temp_allocator.free(temps[1])
        return code, temps

    def if_else_byte_end(self, cell_offset, temps):
        code = self.increment_byte(temps[0], -1) \
               + self.while_byte_end(temps[0])
        self.temp_allocator.free(*temps)
        return code

    def if_not_byte_if(self, cell_offset):
        if_code, temps = self.if_else_byte_if(cell_offset)
        else_code, temps = self.if_else_byte_else(cell_offset, temps)
        return (if_code + else_code), temps

    if_not_byte_end = if_else_byte_end

    def carry_check(self, cell_offset, carry_depth, sign=1):
        if carry_depth == 0:
            return ''
        code_list = []
        if sign == -1:  # byte is 255 on carry
            code_list.append(self.increment_byte(cell_offset, 1))
        if_code, if_temps = self.if_not_byte_if(cell_offset)
        code_list.append(if_code)
        code_list.append(self.increment_byte(cell_offset - 1, sign))
        code_list.append(self.carry_check(cell_offset - 1, carry_depth - 1, sign))
        code_list.append(self.if_not_byte_end(cell_offset, if_temps))
        if sign == -1:
            code_list.append(self.increment_byte(cell_offset, -1))
        return ''.join(code_list)

    def add_byte(self, to_byte, from_byte, carry, sign=1):
        """
        to_offset += from_offset
        from_offset = 0
        if sign==-1, to_offset -= from_offset
        Using sign is faster than negating from_byte in the case of small from_byte
        Value overflows will be carried carry bytes to the left of from_byte
        """
        return ''.join([
            self.while_byte_start(from_byte),
            self.increment_byte(from_byte, -1),
            self.increment_byte(to_byte, sign),
            self.carry_check(to_byte, carry, sign),
            self.while_byte_end(from_byte)
        ])

    def add_num(self, to_offset, from_offset, sign=1):
        """
        to_offset += from_offset
        from_offset = 0
        substracts if sign=-1
        """
        return ''.join(self.add_byte(to_offset + i, from_offset + i, i, sign) for i in range(self.num_size - 1, -1, -1))

    def add_num_preserving(self, to_offset, from_offset):
        """
        to_offset += from_offset
        """
        temp = self.temp_allocator.alloc_temp()
        code = [
            self.copy_byte(from_offset, temp),
            self.add_num(to_offset, temp),
        ]
        self.temp_allocator.free(temp)
        return ''.join(code)

    def sub_byte(self, to_byte, from_byte):
        """
        to_byte -= from_byte
        from_byte = 0
        no carry
        """
        return ''.join([
            self.while_byte_start(from_byte),
            self.increment_byte(from_byte, -1),
            self.increment_byte(to_byte, -1),
            self.while_byte_end(from_byte)
        ])

    def sub_num(self, to_num, from_num):
        """
        to_num -= from_num
        from_num = 0
        """
        return ''.join([
            self.add_num(to_num, from_num, sign=-1)
        ])

    def sub_byte_preserving(self, to_num, from_num):
        """
        to_byte -= from_byte
        """
        temp = self.temp_allocator.alloc_temp()
        code = [
            self.copy_byte(from_num, temp),
            self.sub_byte(to_num, temp),
        ]
        self.temp_allocator.free(temp)
        return ''.join(code)

    def sub_num_preserving(self, to_num, from_num):
        """
        to_num -= from_num
        """
        temp = self.temp_allocator.alloc_temp()
        code = [
            self.copy_num(from_num, temp),
            self.sub_num(to_num, temp),
        ]
        self.temp_allocator.free(temp)
        return ''.join(code)

    def binary_not_byte(self, byte_offset):
        code = []
        temp = self.temp_allocator.alloc_temp()
        code.append(self.move_byte(byte_offset, temp))
        code.append(self.set_byte(byte_offset, self.cell_range - 1))
        code.append(self.sub_byte(byte_offset, temp))
        self.temp_allocator.free(temp)
        return ''.join(code)

    def binary_not_num(self, num_offset):
        return ''.join([self.binary_not_byte(num_offset + i) for i in range(self.num_size)])

    def negate_num(self, num_offset):
        """
        two's complement negation
        """
        return ''.join([
            self.binary_not_num(num_offset),
            self.increment_num(num_offset, 1)
        ])

    def increment_num(self, num_offset, delta):
        """
        Can be made much faster for 0 <= delta < num_size
        """
        temp = self.temp_allocator.alloc_temp()
        code = []
        if delta > 0:
            code.append(self.set_num(temp, delta))
            code.append(self.add_num(num_offset, temp))
        else:
            code.append(self.set_num(temp, -delta))
            code.append(self.sub_num(num_offset, temp))
        self.temp_allocator.free(temp)
        return ''.join(code)

    def less_byte(self, left_byte, right_byte, result_byte):
        temps = self.temp_allocator.alloc_temps(2)
        code = [
            self.clear_byte(result_byte),
            self.copy_byte(right_byte, temps[1]),
            self.copy_byte(left_byte, temps[0]),
            self.while_byte_start(temps[1]),
            self.increment_byte(temps[1], -1)
        ]
        if_code, if_temps = self.if_not_byte_if(temps[0])
        code.append(if_code)
        code.append(self.set_byte(result_byte, 1))
        code.append(self.if_not_byte_end(temps[0], if_temps))
        code.append(self.increment_byte(temps[0], -1))
        code.append(self.while_byte_end(temps[1]))
        self.temp_allocator.free(*temps)
        return ''.join(code)

    def less_num(self, left_num, right_num, result_byte, bytes_left=None):
        if bytes_left is None:
            bytes_left = self.num_size
        if bytes_left == 1:
            return self.less_byte(left_num, right_num, result_byte)
        code = []
        code.append(self.less_byte(left_num, right_num, result_byte))
        if_code, if_temps = self.if_not_byte_if(result_byte)
        code.append(if_code)
        equal_temp = self.temp_allocator.alloc_temp()
        code.append(self.equal_byte(left_num, right_num, equal_temp))
        if_equal_code, if_equal_temps = self.if_else_byte_if(equal_temp)
        code.append(if_equal_code)
        code.append(self.less_num(left_num + 1, right_num + 1, result_byte, bytes_left - 1))
        if_equal_code, if_equal_temps = self.if_else_byte_else(equal_temp, if_equal_temps)
        code.append(if_equal_code)
        code.append(self.set_byte(result_byte, 0))
        code.append(self.if_else_byte_end(equal_temp, if_equal_temps))
        self.temp_allocator.free(equal_temp)
        code.append(self.if_not_byte_end(result_byte, if_temps))
        # code.append('{mem there}')
        return ''.join(code)

    def greater_equal_zero_byte(self, input_byte, result_byte):
        """
        if input_byte > 0:
            result_byte = 1
        else:
            result_byte = 0
        """
        if_code, if_temps = self.if_else_byte_if(input_byte)
        return ''.join([
            if_code,
            self.set_byte(result_byte, 1),
            self.if_else_byte_else(input_byte, if_temps),
            self.set_byte(result_byte, 0),
            self.if_else_byte_end(input_byte, if_temps)
        ])

    def logic_and_bytes(self, byte_a, byte_b, result_byte):
        code = [self.set_byte(result_byte, 0)]
        if_a_code, temp_a = self.if_byte_if(byte_a)
        if_b_code, temp_b = self.if_byte_if(byte_b)
        code += [
            if_a_code,
            if_b_code,
            self.set_byte(result_byte, 1),
            self.if_byte_end(byte_b, temp_b),
            self.if_byte_end(byte_a, temp_a)
        ]
        return ''.join(code)

    def logic_not_byte(self, byte_offset):
        if_code, temp = self.if_byte_if(byte_offset)
        code = [if_code,
                self.increment_byte(byte_offset, -2),
                self.if_byte_end(byte_offset, temp),
                self.increment_byte(byte_offset, 1)]
        return ''.join(code)

    def logic_or_bytes(self, byte_a, byte_b, result_byte):
        code = [self.set_byte(result_byte, 0)]
        if_a_code, temp_a = self.if_byte_if(byte_a)
        code += [
            if_a_code,
            self.set_byte(result_byte, 1),
            self.if_byte_end(byte_a, temp_a)
        ]
        if_b_code, temp_b = self.if_byte_if(byte_b)
        code += [
            if_b_code,
            self.set_byte(result_byte, 1),
            self.if_byte_end(byte_b, temp_b)
        ]
        return ''.join(code)

    def equal_byte(self, left_byte, right_byte, result_byte):
        temps = self.temp_allocator.alloc_temps(1)
        code = [
            self.clear_byte(result_byte),
            self.copy_byte(left_byte, temps[0]),
            self.sub_byte_preserving(temps[0], right_byte)
        ]
        if_code, if_temps = self.if_not_byte_if(temps[0])
        code.append(if_code)
        code.append(self.set_byte(result_byte, 1))
        code.append(self.if_not_byte_end(temps[0], if_temps))
        self.temp_allocator.free(*temps)
        return ''.join(code)

    def equal_num(self, left_num, right_num, result_byte, bytes_left=None):
        if bytes_left is None:
            bytes_left = self.num_size
        if bytes_left == 1:
            return self.equal_byte(left_num, right_num, result_byte)
        code = [self.equal_byte(left_num, right_num, result_byte)]
        if_code, temp = self.if_byte_if(result_byte)
        code.append(if_code)
        code.append(self.equal_num(left_num + 1, right_num + 1, result_byte, bytes_left - 1))
        code += [self.if_byte_end(result_byte, temp)]
        return ''.join(code)

    def num_is_zero(self, num_offset, result_byte):
        code = [self.set_byte(result_byte, 1)]
        for i in range(self.num_size):
            if_code, if_temps = self.if_byte_if(num_offset + i)
            code.append(if_code)
            code.append(self.clear_byte(result_byte))
            code.append(self.if_byte_end(result_byte, if_temps))
        return ''.join(code)

    def equal_immediate_num(self, num_offset, imm, result_byte):
        temp = self.temp_allocator.alloc_temp()
        code = [self.set_byte(temp, imm),
                self.equal_num(num_offset, temp, result_byte)]
        self.temp_allocator.free(temp)
        return ''.join(code)

    def goto_target_vmc(self):
        temp = self.temp_allocator.alloc_temp()
        code = [
            self.less_num(self.offset_cell_index, self.offset_target_cell, temp),
            self.while_byte_start(temp),
            self.move_k_vmc(1),
            self.less_num(self.offset_cell_index, self.offset_target_cell, temp),
            self.while_byte_end(temp),
            self.less_num(self.offset_target_cell, self.offset_cell_index, temp),
            self.while_byte_start(temp),
            self.move_k_vmc(-1),
            self.less_num(self.offset_target_cell, self.offset_cell_index, temp),
            self.while_byte_end(temp)
        ]
        self.temp_allocator.free(temp)
        return ''.join(code)

    def load_memory(self, address_offset, dest_offset, memory_offset=None):
        if memory_offset is None:
            memory_offset = self.offset_heap_value
        return self.copy_num(address_offset, self.offset_target_cell) + self.goto_target_vmc() \
               + self.copy_num(memory_offset, dest_offset)

    def store_memory(self, address_offset, value_offset, memory_offset=None, value_is_immediate=False):
        if memory_offset is None:
            memory_offset = self.offset_heap_value
        code = self.copy_num(address_offset, self.offset_target_cell) + self.goto_target_vmc()
        if value_is_immediate:
            code += self.set_num(memory_offset, value_offset)
        else:
            code += self.copy_num(value_offset, memory_offset)
        return code

    def opening_code(self):
        # dirty trick to enter the code loop with a positive number
        code = [
            self.set_num(self.offset_cur_cmd, 1),
            self.set_byte(self.offset_flow_reserved, 1),
            self.while_byte_start(self.offset_flow_reserved)
        ]
        return ''.join(code)

    def basic_block_start(self):
        code = [
            self.increment_num(self.offset_cur_cmd, -1),
            self.num_is_zero(self.offset_cur_cmd, self.offset_flow_reserved),
            self.while_byte_start(self.offset_flow_reserved),
        ]
        return ''.join(code)

    def basic_block_end(self):
        return self.clear_byte(self.offset_flow_reserved) + self.while_byte_end(self.offset_flow_reserved)

    def basic_block_goto_next(self, diff=1):
        return self.set_num(self.offset_cur_cmd, diff) + self.basic_block_end()

    def closing_code(self):
        code = [
            self.increment_num(self.offset_cur_cmd, -1),
            self.num_is_zero(self.offset_cur_cmd, self.offset_flow_reserved),
            self.logic_not_byte(self.offset_flow_reserved),
            self.while_byte_end(self.offset_flow_reserved)
        ]
        return ''.join(code)
