from CommandType import CommandType
from Operand import Operand, OperandType
from VMCController import VMCController


def put_value_in_temp(controller: VMCController, operand: Operand):
    """
    If operand is a register, return it's offset
    Otherwise, allocate a temp register, copy operand's value to it and return
    Also return the code created
    """
    if operand.is_register():
        return operand.value, ''
    temp = controller.temp_allocator.alloc_temp()
    return temp, controller.set_num(temp, operand.value)


def force_value_in_temp(controller: VMCController, operand: Operand):
    """
    Copy the value of operand to a new temp register, regardless of whether operand is already a register
    Return the temp and the code
    """
    temp = controller.temp_allocator.alloc_temp()
    if operand.is_immediate():
        code = controller.set_num(temp, operand.value)
    else:
        code = controller.copy_num(operand.value, temp)
    return temp, code


def free_possible_temp(controller: VMCController, operand: Operand, register):
    """
    Free the register returned by put_value_in_temp, if it is temp
    """
    if operand.is_immediate():
        controller.temp_allocator.free(register)


class Command:
    """
    A single ASM command and it's operands
    """

    def __init__(self, command_text, register_list, basic_block_idx):
        """
        Parses a command.
        The command should be without leading or trailing whitespaces, and without comments
        Raises ValueError if the command is invalid
        """
        command_parts = command_text.split()
        self.command_type = CommandType[command_parts[0]]
        self.operands = [Operand(operand, register_list) for operand in command_parts[1:]]
        self.basic_block_idx = basic_block_idx

    def compile(self, controller, label_to_basic_block):
        compile_functions = {
            CommandType.mov: self.compile_mov,
            CommandType.load: self.compile_load,
            CommandType.store: self.compile_store,
            CommandType.neg: self.compile_neg,
            CommandType.add: self.compile_add,
            CommandType.sub: self.compile_sub,
            CommandType.less: self.compile_less,
            CommandType.eq: self.compile_eq,
            CommandType.logic_not: self.compile_logic_not,
            CommandType.logic_and: self.compile_logic_and,
            CommandType.logic_or: self.compile_logic_or,
            CommandType.binary_not: self.compile_binary_not,
            CommandType.push: self.compile_push,
            CommandType.pop: self.compile_pop,
            CommandType.ret: self.compile_ret,
            CommandType.jmp: self.compile_jmp,
            CommandType.label: self.compile_label,
            CommandType.jnz: self.compile_jnz,
            CommandType.call: self.compile_call,
            # CommandType.read = auto()
            # CommandType.write = auto()
        }
        return compile_functions[self.command_type](controller, label_to_basic_block)

    def compile_mov(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 2
        assert self.operands[0].is_register()
        assert not self.operands[1].is_label()
        if self.operands[0] == self.operands[1]:
            return ''
        if self.operands[1].is_immediate():
            return controller.set_num(self.operands[0].value, self.operands[1].value)
        return controller.copy_num(self.operands[1].value, self.operands[0].value)

    def compile_store(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 2
        assert not self.operands[0].is_label()
        assert not self.operands[1].is_label()
        addr_offset, addr_code = put_value_in_temp(controller, self.operands[0])
        if self.operands[1].is_immediate():
            code = addr_code + controller.store_memory(addr_offset, self.operands[1].value, value_is_immediate=True)
        else:
            code = addr_code + controller.store_memory(addr_offset, self.operands[1].value)
        free_possible_temp(controller, self.operands[0], addr_offset)
        return code

    def compile_load(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 2
        assert self.operands[0].is_register()
        assert not self.operands[1].is_label()
        addr_offset, addr_code = put_value_in_temp(controller, self.operands[1])
        code = addr_code + controller.load_memory(addr_offset, self.operands[0].value)
        free_possible_temp(controller, self.operands[1], addr_offset)
        return code

    def compile_neg(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_register()
        return controller.negate_num(self.operands[0].value)

    def compile_add(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 3
        assert self.operands[0].is_register()
        assert not self.operands[1].is_label()
        assert not self.operands[2].is_label()
        if self.operands[1].is_immediate() and self.operands[2].is_immediate():
            return controller.set_num(self.operands[0].value, self.operands[1].value + self.operands[2].value)
        if self.operands[1].value == self.operands[0].value and self.operands[2].is_immediate():
            return controller.increment_num(self.operands[0].value, self.operands[2].value)
        if self.operands[2].value == self.operands[0].value and self.operands[1].is_immediate():
            return controller.increment_num(self.operands[0].value, self.operands[1].value)
        lhs_temp, lhs_code = force_value_in_temp(controller, self.operands[1])
        rhs_temp, rhs_code = force_value_in_temp(controller, self.operands[2])
        first_copy = controller.move_num(lhs_temp, self.operands[0].value)
        controller.temp_allocator.free(lhs_temp)
        add_code = controller.add_num(self.operands[0].value, rhs_temp)
        controller.temp_allocator.free(rhs_temp)
        return lhs_code + rhs_code + first_copy + add_code

    def compile_sub(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 3
        assert self.operands[0].is_register()
        assert not self.operands[1].is_label()
        assert not self.operands[2].is_label()
        if self.operands[1].is_immediate() and self.operands[2].is_immediate():
            return controller.set_num(self.operands[0].value, self.operands[1].value - self.operands[2].value)
        if self.operands[1].value == self.operands[0].value and self.operands[2].is_immediate():
            return controller.increment_num(self.operands[0].value, -self.operands[2].value)
        lhs_temp, lhs_code = force_value_in_temp(controller, self.operands[1])
        rhs_temp, rhs_code = force_value_in_temp(controller, self.operands[2])
        first_copy = controller.move_num(lhs_temp, self.operands[0].value)
        controller.temp_allocator.free(lhs_temp)
        add_code = controller.sub_num(self.operands[0].value, rhs_temp)
        controller.temp_allocator.free(rhs_temp)
        return lhs_code + rhs_code + first_copy + add_code

    def compile_less(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 3
        assert self.operands[0].is_register()
        assert not self.operands[1].is_label()
        assert not self.operands[2].is_label()
        result_byte = self.operands[0].value + controller.num_size - 1
        if self.operands[1].is_immediate() and self.operands[2].is_immediate():
            if self.operands[1].value < self.operands[2].value:
                return controller.clear_num(self.operands[0].value) + controller.set_byte(result_byte, 1)
            else:
                return controller.clear_num(self.operands[0].value) + controller.set_byte(result_byte, 0)
        lhs_temp, lhs_code = force_value_in_temp(controller, self.operands[1])
        rhs_temp, rhs_code = force_value_in_temp(controller, self.operands[2])
        clear_code = controller.clear_num(self.operands[0].value)
        less_code = controller.less_num(lhs_temp, rhs_temp, result_byte)
        controller.temp_allocator.free(lhs_temp, rhs_temp)
        return lhs_code + rhs_code + clear_code + less_code

    def compile_eq(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 3
        assert self.operands[0].is_register()
        assert not self.operands[1].is_label()
        assert not self.operands[2].is_label()
        result_byte = self.operands[0].value + controller.num_size - 1
        if self.operands[1].is_immediate() and self.operands[2].is_immediate():
            if self.operands[1].value == self.operands[2].value:
                return controller.clear_num(self.operands[0].value) + controller.set_byte(result_byte, 1)
            else:
                return controller.clear_num(self.operands[0].value) + controller.set_byte(result_byte, 0)
        lhs_temp, lhs_code = force_value_in_temp(controller, self.operands[1])
        rhs_temp, rhs_code = force_value_in_temp(controller, self.operands[2])
        clear_code = controller.clear_num(self.operands[0].value)
        less_code = controller.equal_num(lhs_temp, rhs_temp, result_byte)
        controller.temp_allocator.free(lhs_temp, rhs_temp)
        return lhs_code + rhs_code + clear_code + less_code

    def compile_logic_not(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_register()
        result_byte = self.operands[0].value + controller.num_size - 1
        return controller.logic_not_byte(result_byte)

    def compile_logic_and(self, controller: VMCController, label_to_basic_block):
        """
        TODO: This can be made much much more efficient
        """
        assert len(self.operands) == 3
        assert self.operands[0].is_register()
        assert self.operands[1].is_register()
        assert self.operands[2].is_register()
        boolean_offset = controller.num_size - 1
        if self.operands[1].value == self.operands[2].value:
            if self.operands[0].value == self.operands[1].value:
                return ''
            else:
                return controller.copy_byte(self.operands[1].value + boolean_offset, self.operands[0].value + boolean_offset)
        lhs_temp, lhs_code = force_value_in_temp(controller, self.operands[1])
        rhs_temp, rhs_code = force_value_in_temp(controller, self.operands[2])
        clear_code = controller.clear_num(self.operands[0].value)
        and_code = controller.logic_and_bytes(lhs_temp + boolean_offset, rhs_temp + boolean_offset, self.operands[0].value + boolean_offset)
        controller.temp_allocator.free(lhs_temp, rhs_temp)
        return lhs_code + rhs_code + clear_code + and_code

    def compile_logic_or(self, controller: VMCController, label_to_basic_block):
        """
        TODO: This can be made much much more efficient
        """
        assert len(self.operands) == 3
        assert self.operands[0].is_register()
        assert self.operands[1].is_register()
        assert self.operands[2].is_register()
        boolean_offset = controller.num_size - 1
        if self.operands[1].value == self.operands[2].value:
            if self.operands[0].value == self.operands[1].value:
                return ''
            else:
                return controller.copy_byte(self.operands[1].value + boolean_offset, self.operands[0].value + boolean_offset)
        lhs_temp, lhs_code = force_value_in_temp(controller, self.operands[1])
        rhs_temp, rhs_code = force_value_in_temp(controller, self.operands[2])
        clear_code = controller.clear_num(self.operands[0].value)
        and_code = controller.logic_or_bytes(lhs_temp + boolean_offset, rhs_temp + boolean_offset, self.operands[0].value + boolean_offset)
        controller.temp_allocator.free(lhs_temp, rhs_temp)
        return lhs_code + rhs_code + clear_code + and_code

    def compile_binary_not(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_register()
        return controller.binary_not_num(self.operands[0].value)

    def compile_push(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert not self.operands[0].is_label()
        push_code = controller.store_memory(controller.offset_stack_pointer, self.operands[0].value, controller.offset_stack_value, self.operands[0].is_immediate())
        return push_code + controller.increment_num(controller.offset_stack_pointer, 1)

    def compile_pop(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_register()
        dec_code = controller.increment_num(controller.offset_stack_pointer, -1)
        pop_code = controller.load_memory(controller.offset_stack_pointer, self.operands[0].value, controller.offset_stack_value)
        return dec_code + pop_code

    def compile_label(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_label()
        return controller.basic_block_goto_next()

    def calculate_basic_block_diff(self, label_to_basic_block, target):
        label_bb = label_to_basic_block[target]
        if label_bb > self.basic_block_idx:
            diff = label_bb - self.basic_block_idx
        else:
            diff = label_to_basic_block['exit'] - self.basic_block_idx + label_bb + 1
        return diff

    def compile_jmp(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_label()
        diff = self.calculate_basic_block_diff(label_to_basic_block, self.operands[0].value)
        return controller.basic_block_goto_next(diff)

    def compile_jnz(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 2
        assert self.operands[0].is_register()
        assert self.operands[1].is_label()
        diff = self.calculate_basic_block_diff(label_to_basic_block, self.operands[1].value)
        code = [controller.set_num(controller.offset_cur_cmd, 1),
                controller.num_is_zero(self.operands[0].value, controller.offset_flow_reserved),
                controller.logic_not_byte(controller.offset_flow_reserved)]
        if_code, if_temps = controller.if_byte_if(controller.offset_flow_reserved)
        code.append(if_code)
        code.append(controller.set_num(controller.offset_cur_cmd, diff))
        code.append(controller.if_byte_end(controller.offset_flow_reserved, if_temps))
        code.append(controller.basic_block_end())
        return ''.join(code)

    def compile_call(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 1
        assert self.operands[0].is_label()
        diff = self.calculate_basic_block_diff(label_to_basic_block, self.operands[0].value)
        code = [controller.store_memory(controller.offset_stack_pointer, self.basic_block_idx + 1,
                                        memory_offset=controller.offset_stack_value, value_is_immediate=True),
                controller.increment_num(controller.offset_stack_pointer, 1),
                controller.basic_block_goto_next(diff)]
        return ''.join(code)

    def compile_ret(self, controller: VMCController, label_to_basic_block):
        assert len(self.operands) == 0
        target_bb_temp, source_bb_temp, exit_bb_temp = controller.temp_allocator.alloc_temps(3)
        code = [controller.increment_num(controller.offset_stack_pointer, -1),
                controller.load_memory(controller.offset_stack_pointer, target_bb_temp, controller.offset_stack_value),
                controller.set_num(source_bb_temp, self.basic_block_idx),
                controller.set_num(exit_bb_temp, label_to_basic_block['exit']),
                controller.less_num(source_bb_temp, target_bb_temp, controller.offset_flow_reserved),
                controller.sub_num(target_bb_temp, source_bb_temp)]
        if_code, if_temps = controller.if_not_byte_if(controller.offset_flow_reserved)
        code += [
            if_code,
            controller.add_num(target_bb_temp, exit_bb_temp),
            controller.increment_num(target_bb_temp, 1),
            controller.if_not_byte_end(controller.offset_flow_reserved, if_temps),
            controller.move_num(target_bb_temp, controller.offset_cur_cmd),
            controller.basic_block_end()
        ]
        controller.temp_allocator.free(target_bb_temp, source_bb_temp, exit_bb_temp)
        return ''.join(code)
