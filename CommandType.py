from enum import Enum, auto


class CommandType(Enum):
    mov = auto()
    load = auto()
    store = auto()
    neg = auto()
    add = auto()
    sub = auto()
    less = auto()
    eq = auto()
    logic_not = auto()
    logic_and = auto()
    logic_or = auto()
    binary_not = auto()
    push = auto()
    pop = auto()
    ret = auto()
    jmp = auto()
    label = auto()
    jnz = auto()
    call = auto()
    read = auto()
    write = auto()

    def ends_basic_block(self):
        """
        Does this command end it's basic block?
        """
        return self in [CommandType.ret, CommandType.jmp, CommandType.label, CommandType.jnz, CommandType.call]
