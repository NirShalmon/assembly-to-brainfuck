from BrainfuckInterpreter import BrainfuckInterpreter
from VMCController import VMCController


class Debugger:

    def __init__(self, vmc_controller, code):
        self.vmc_controller = vmc_controller
        self.interpreter = BrainfuckInterpreter(code, vmc_controller.cell_range)
        self.vmc_idx = 0
        self.commands_executed = 0
        self.execution_completed = False

    def exec_commands(self, max_amount=999999999999999):
        """
        Execute at most max_amount commands
        """
        for i in range(max_amount):
            amount_executed, flags = self.interpreter.exec_commands(1)
            self.commands_executed += amount_executed
            if amount_executed == 0:
                self.execution_completed = True
                break;
            for flag in flags:
                self.process_flag(flag)

    def print_vmc_cell(self):
        """
        Prints the current vmc cell's registers
        """
        print(f'Data pointer: {self.interpreter.data_pointer}')
        for register in self.vmc_controller.register_list.register_list:
            offset = self.vmc_controller.register_list.get_register_offset(register.name)
            print(f'{register.name}: {self.get_vmc_value(offset)}')
        print()

    def process_flag(self, flag):
        """
        Process a debug flag
        """
        if flag.split()[0] == 'move_vmc':
            self.vmc_idx += int(flag.split()[1])
        elif flag.split()[0] == 'mem':
            self.print_vmc_cell()
        elif flag.split()[0] == 'print':
            print(flag[flag.find(' ') + 1:])
        else:
            raise Exception("Unrecognized flag")

    def parse_num_unsigned(self, first_cell):
        """
        Parse an unsigned num from the program's memory, starting at first_cell
        """
        result = 0
        for i in range(self.vmc_controller.num_size):
            mem_value = 0
            if first_cell + i < len(self.interpreter.memory):
                mem_value = self.interpreter.memory[first_cell + i]
            result += mem_value * (self.vmc_controller.cell_range ** (self.vmc_controller.num_size - i - 1))
        return result

    def parse_num_signed(self, first_cell):
        unsigned_num = self.parse_num_unsigned(first_cell)
        if unsigned_num >= (self.vmc_controller.cell_range ** self.vmc_controller.num_size) / 2:
            return unsigned_num - self.vmc_controller.cell_range ** self.vmc_controller.num_size
        return unsigned_num

    def get_memory(self, address, as_signed_num=False):
        """
        Return the value at a given memory address
        """
        first_cell = address * self.vmc_controller.vmc_size + self.vmc_controller.offset_heap_value
        return self.parse_num_signed(first_cell) if as_signed_num else self.parse_num_unsigned(first_cell)

    def get_vmc_value(self, offset, as_signed_num=False):
        """
        Return the value at a offset from the current vmc
        """
        first_cell = self.vmc_idx * self.vmc_controller.vmc_size + offset
        return self.parse_num_signed(first_cell) if as_signed_num else self.parse_num_unsigned(first_cell)

    def full_debug_print(self):
        print([self.get_memory(i) for i in range(100)])
        self.print_vmc_cell()
