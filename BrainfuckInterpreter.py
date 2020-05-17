import sys


class BrainfuckInterpreter:

    def __init__(self, code, cell_range):
        self.code = code
        self.memory = []
        self.instruction_pointer = 0
        self.data_pointer = 0
        self.cell_range = cell_range
        self.while_mapper = self.map_whiles()

    """
    Create a dictionary to map indexes of [ and ] to the corresponding indexes
    """

    def map_whiles(self):
        while_mapper = {}
        while_stack = []
        for idx, cmd in enumerate(self.code):
            if cmd == '[':
                while_stack.append(idx)
            elif cmd == ']':
                if len(while_stack) == 0:
                    raise Exception("Matching '[' not found")
                while_mapper[idx] = while_stack[-1]
                while_mapper[while_stack[-1]] = idx
                while_stack.pop()
        if len(while_stack) > 0:
            raise Exception("Matching ']' not found")
        return while_mapper

    """
    Execute at most max_amount commands. Return amount of commands exe
    Also returns a list of debug flags passed.
    """

    def exec_commands(self, max_amount=1):
        debug_flags = []
        for i in range(max_amount):
            if self.instruction_pointer < len(self.code) and self.code[self.instruction_pointer] == '{':
                debug_flags.append(self.read_debug_flag())
                continue
            if self.instruction_pointer >= len(self.code):
                return i, debug_flags
            if self.data_pointer == len(self.memory):
                self.memory += [0] * 10000
            instruction_map = {'+': self.inc_data, '-': self.dec_data, '>': self.move_right, '<': self.move_left,
                               ',': self.input_cell, '.': self.print_cell, '[': self.while_start, ']': self.while_end}
            if self.code[self.instruction_pointer] in instruction_map:
                instruction_map[self.code[self.instruction_pointer]]()
            else:
                raise Exception(f"Unrecognized symbol {self.code[self.instruction_pointer]} in code")
        return max_amount, debug_flags

    """
    Read and return a debug flag from the code
    """

    def read_debug_flag(self):
        flag_end = self.code.find('}', self.instruction_pointer)
        flag = self.code[self.instruction_pointer + 1: flag_end]
        self.instruction_pointer = flag_end + 1
        return flag

    """
    Brainfuck +
    """

    def inc_data(self):
        self.memory[self.data_pointer] += 1
        if self.memory[self.data_pointer] == self.cell_range:
            self.memory[self.data_pointer] = 0
        self.instruction_pointer += 1

    """
    Brainfuck -
    """

    def dec_data(self):
        self.memory[self.data_pointer] -= 1
        if self.memory[self.data_pointer] == -1:
            self.memory[self.data_pointer] = self.cell_range - 1
        self.instruction_pointer += 1

    """
    Brainfuck >
    """

    def move_right(self):
        self.data_pointer += 1
        self.instruction_pointer += 1

    """
    Brainfuck <
    """

    def move_left(self):
        if self.data_pointer == 0:
            raise Exception("Negative data pointer!")
        self.data_pointer -= 1
        self.instruction_pointer += 1

    """
    Brainfuck .
    """

    def print_cell(self):
        sys.stdout.write(chr(self.memory[self.data_pointer]))
        self.instruction_pointer += 1

    """
    Brainfuck ,
    """

    def input_cell(self):
        self.memory[self.data_pointer] = sys.stdin.read(1)

    """
    Brainfuck [
    """

    def while_start(self):
        if self.memory[self.data_pointer] > 0:
            self.instruction_pointer += 1
        else:
            self.instruction_pointer = self.while_mapper[self.instruction_pointer] + 1

    """
    Brainfuck ]
    """

    def while_end(self):
        if self.memory[self.data_pointer] == 0:
            self.instruction_pointer += 1
        else:
            self.instruction_pointer = self.while_mapper[self.instruction_pointer] + 1
