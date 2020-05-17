from BrainfuckInterpreter import BrainfuckInterpreter
from VMCController import VMCController


class Debugger:

    def __init__(self, vmc_controller, code):
        self.vmc_controller = vmc_controller
        self.interpreter = BrainfuckInterpreter(code, vmc_controller.cell_range)
        self.vmc_idx = 0
        self.commands_executed = 0
        self.execution_completed = False

    """
    Execute at most max_amount commands
    """

    def exec_commands(self, max_amount=999999999999999):
        for i in range(max_amount):
            amount_executed, flags = self.interpreter.exec_commands(1)
            self.commands_executed += amount_executed
            if amount_executed == 0:
                self.execution_completed = True
                break;
            for flag in flags:
                self.process_flag(flag)

    """
    Prints the current vmc cell's registers
    """
    def print_vmc_cell(self):
        print(f'Data pointer: {self.interpreter.data_pointer}')
        for register in self.vmc_controller.register_list.register_list:
            offset = self.vmc_controller.register_list.get_register_offset(register.name)
            print(f'{register.name}: {self.get_vmc_value_unsigned(offset)}')
        print()

    """
    Process a debug flag
    """

    def process_flag(self, flag):
        if flag.split()[0] == 'move_vmc':
            self.vmc_idx += int(flag.split()[1])
        elif flag.split()[0] == 'mem':
            self.print_vmc_cell()
        elif flag.split()[0] == 'print':
            print(flag[flag.find(' ') + 1:])
        else:
            raise Exception("Unrecognized flag")

    """
    Parse an unsigned num from the program's memory, starting at first_cell
    """

    def parse_num_unsigned(self, first_cell):
        result = 0
        for i in range(self.vmc_controller.num_size):
            mem_value = 0
            if first_cell + i < len(self.interpreter.memory):
                mem_value = self.interpreter.memory[first_cell + i]
            result += mem_value * (self.vmc_controller.cell_range ** (self.vmc_controller.num_size - i - 1))
        return result

    """
    Return the value at a given memory address as a unsigned int
    """

    def get_memory_unsigned(self, address):
        return self.parse_num_unsigned(address * self.vmc_controller.vmc_size + self.vmc_controller.offset_heap_value)

    """
    Return the value at a offset from the current vmc as a unsigned int
    """

    def get_vmc_value_unsigned(self, offset):
        return self.parse_num_unsigned(self.vmc_idx * self.vmc_controller.vmc_size + offset)

    def full_debug_print(self):
        print([self.get_memory_unsigned(i) for i in range(100)])
        self.print_vmc_cell()
