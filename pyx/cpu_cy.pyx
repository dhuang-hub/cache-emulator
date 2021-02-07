

cdef class CPU:
    cdef object cache
    cdef readonly int instructionCount

    def __init__(self, cache):
        self.cache = cache
        self.instructionCount = 0

    cpdef double loadDouble(self, int address):
        self.instructionCount += 1
        return self.cache.getDouble(address)

    cpdef void storeDouble(self, int address, double value):
        self.instructionCount += 1
        self.cache.setDouble(address, value)

    cpdef double addDouble(self, double value1, double value2):
        self.instructionCount += 1
        return value1 + value2

    cpdef double multDouble(self, double value1, double value2):
        self.instructionCount += 1
        return value1 * value2
