class Register:
    """
    A register is public if it can be accessed by compiled ASM.
    It will only be copied between VMCs if it is_preserved
    Support may later be added for variable sized registers
    """

    def __init__(self, name, is_preserved, is_public, size):
        self.name = name
        self.is_public = is_public
        self.size = size
        self.is_preserved = is_preserved


class RegisterList:

    def __init__(self, register_list):
        self.register_list = register_list

    def get_register_offset(self, name, public_only=False):
        """
        If register name is found, and matches the public_only setting, than returns it's offset in the VMC.
        Otherwise, raises Exception
        """
        total_offset = 0
        for register in self.register_list:
            if register.name == name:
                if not public_only or register.is_public:
                    return total_offset
                else:
                    raise Exception("Register is not public")
            total_offset += register.size
        raise Exception("Register not found")

    def total_size(self):
        """
        The sum of sizes of registers
        """
        return sum([reg.size for reg in self.register_list])

    def get_preserved_offsets(self):
        """
        Returns the offsets of the preserved registers
        """
        preserved_offsets = []
        for register in self.register_list:
            if register.is_preserved:
                preserved_offsets.append(self.get_register_offset(register.name))
        return preserved_offsets

