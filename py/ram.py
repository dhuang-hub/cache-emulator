from numpy import zeros
from math import log2


class RAM:
    def __init__(self, dataSize, blockSize, wordSize=8):
        blockBits = int(log2(blockSize))
        i = (dataSize + blockSize - 1) // blockSize
        j = blockSize // wordSize

        self.data      = zeros((i, j))
        self.dataSize  = dataSize
        self.blockSize = blockSize
        self.blockBits = blockBits

    # getBlock
    def __getitem__(self, address):
        return self.data[address >> self.blockBits, :]

    # setBlock
    def __setitem__(self, address, block):
        self.data[address >> self.blockBits, :] = block
