from enum import Enum, auto


class CommandType(Enum):
    mov = auto
    load = auto
    store = auto
    neg = auto
    add = auto
    sub = auto
    less = auto
    eq = auto
    logic_not = auto
    logic_and = auto
    logic_or = auto
    binary_not = auto
    push = auto
    pop = auto
    ret = auto
    jmp = auto
    label = auto
    jnz = auto
    call = auto
    read = auto
    write = auto

    @classmethod
    def parse(cls, cmd):
        parsing_dict = {'mov': CommandType.mov,
                        'load': CommandType.load,
                        'store': CommandType.store,
                        'neg': CommandType.neg,
                        'add': CommandType.add,
                        'sub': CommandType.sub,
                        'less': CommandType.less,
                        'eq': CommandType.eq,
                        'logic_not': CommandType.logic_not,
                        'logic_and': CommandType.logic_and,
                        'logic_or': CommandType.logic_or,
                        'binary_not': CommandType.binary_not,
                        'push': CommandType.push,
                        'pop': CommandType.pop,
                        'ret': CommandType.ret,
                        'jmp': CommandType.jmp,
                        'label': CommandType.label,
                        'jnz': CommandType.jnz,
                        'call': CommandType.call,
                        'read': CommandType.read,
                        'write': CommandType.write}
        if cmd in parsing_dict:
            return parsing_dict[cmd]
        raise ValueError('Invalid command')

    def ends_basic_block(self):
        """
        Does this command end it's basic block?
        """
        return self in [CommandType.ret, CommandType.jmp, CommandType.label, CommandType.jnz, CommandType.call]
