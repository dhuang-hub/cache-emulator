from math import log2
import numpy as np
cimport numpy as np
cimport cython


cdef class RAM:
    cdef readonly np.ndarray data
    cdef readonly int dataSize, blockSize, blockBits

    def __init__(self, int dataSize, int blockSize, int wordSize=8):
        blockBits = int(log2(blockSize))
        i = (dataSize + blockSize - 1) // blockSize
        j = blockSize // wordSize

        self.data      = np.zeros((i, j))
        self.dataSize  = dataSize
        self.blockSize = blockSize
        self.blockBits = blockBits

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef np.ndarray[np.double_t, ndim=1] getBlock(self, int address):
        return self.data[address >> self.blockBits, :]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef void setBlock(self, int address, np.ndarray[np.double_t, ndim=1] block):
        self.data[address >> self.blockBits, :] = block
