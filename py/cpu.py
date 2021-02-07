

class CPU:
    def __init__(self, cache):
        self.cache = cache
        self.instructionCount = 0

    # loadDouble
    def __getitem__(self, address):
        self.instructionCount += 1
        return self.cache[address]

    # storeDouble
    def __setitem__(self, address, value):
        self.instructionCount += 1
        self.cache[address] = value

    def addDouble(self, value1, value2):
        self.instructionCount += 1
        return value1 + value2

    def multDouble(self, value1, value2):
        self.instructionCount += 1
        return value1 * value2
