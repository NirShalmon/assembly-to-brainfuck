class TempAllocator:

    def __init__(self, vmc_size, temp_offsets):
        self.vmc_size = vmc_size
        self.temp_offsets = temp_offsets
        self.temp_id_allocated = []
        self.max_temp_used = 0

    def free_all(self):
        self.temp_id_allocated.clear()

    def temp_id_to_offset(self, temp_id):
        return (temp_id // len(self.temp_offsets)) * self.vmc_size + self.temp_offsets[temp_id % len(self.temp_offsets)]

    def temp_offset_to_id(self, temp_offset):
        # inefficient but super versatile implementation
        id = 0
        while self.temp_id_to_offset(id) < temp_offset:
            id += 1
        return id

    def free(self, *temp_offsets):
        for temp_offset in temp_offsets:
            self.temp_id_allocated[self.temp_offset_to_id(temp_offset)] = False

    def alloc_temp(self):
        for i in range(len(self.temp_id_allocated)):
            if not self.temp_id_allocated[i]:
                self.temp_id_allocated[i] = True
                return self.temp_id_to_offset(i)
        self.temp_id_allocated.append(True)
        self.max_temp_used = max(self.max_temp_used, len(self.temp_id_allocated))
        return self.temp_id_to_offset(len(self.temp_id_allocated) - 1)

    def alloc_temps(self, amount):
        return tuple(self.alloc_temp() for i in range(amount))