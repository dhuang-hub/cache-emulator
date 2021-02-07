from math import log2
from random import randrange
import numpy as np
cimport numpy as np
# cimport cython


cdef class Cache:
    cdef object ram
    cdef readonly int wordBits, cacheBits, blockBits, blockMask, setBits, setMask, nAssociativity, wordsPerBlock
    cdef readonly int readHit, readMiss, writeHit, writeMiss
    cdef np.ndarray openSetSlots, data
    cdef str replacement
    cdef list replacementQueue
    cdef bint isRandomReplace

    def __init__(self, ram, cacheSize, blockSize, nAssociativity, replacement='LRU', wordSize=8):
        wordBits      = int(log2(wordSize))
        cacheBits     = int(log2(cacheSize))
        blockBits     = int(log2(blockSize))
        setBits       = cacheBits - blockBits - int(log2(nAssociativity))
        wordsPerBlock = 1 << (blockBits - wordBits)

        # cache attributes
        self.ram              = ram
        self.wordBits         = wordBits
        self.cacheBits        = cacheBits
        self.blockBits        = blockBits
        self.blockMask        = (1 << blockBits) - 1
        self.setBits          = setBits
        self.setMask          = (1 << setBits) - 1
        self.wordsPerBlock    = wordsPerBlock
        self.nAssociativity   = nAssociativity
        self.openSetSlots     = np.full(1 << setBits, nAssociativity, dtype='i4')
        self.data             = np.zeros((1 << setBits, nAssociativity * wordsPerBlock))
        self.replacement      = replacement if nAssociativity > 1 else None
        self.replacementQueue = [dict() for _ in range(1 << setBits)]
        self.isRandomReplace  = True if self.replacement == 'random' else False

        # event log
        self.readHit   = 0
        self.readMiss  = 0
        self.writeHit  = 0
        self.writeMiss = 0

    cdef (int, int, int) parseAddress(self, int address):
        offset   = (address & self.blockMask) >> self.wordBits
        address  = address >> self.blockBits
        tag      = address >> self.setBits
        setIdx   = address & self.setMask
        return tag, setIdx, offset

    cdef int _replace(self, int tag, int setIdx):
        # assert tag not in self.replacementQueue[setIdx]
        # assert len(self.replacementQueue[setIdx]) == self.nAssociativity
        if self.isRandomReplace:
            oldTag = list(self.replacementQueue[setIdx])[randrange(self.nAssociativity)]
        else:
            oldTag = next(iter(self.replacementQueue[setIdx]))
        slotIdx = self.replacementQueue[setIdx].pop(oldTag)
        self.replacementQueue[setIdx][tag] = slotIdx
        return slotIdx

    cdef (int, int, int) _getBlock(self, int address, bint isWrite):
        cdef int tag, setIdx, offset, slotIdx
        tag, setIdx, offset = self.parseAddress(address)
        if tag in self.replacementQueue[setIdx]:                     # HIT
            if isWrite:
                self.writeHit += 1
            else:
                self.readHit += 1
            slotIdx = self.replacementQueue[setIdx][tag]             # HIT - Get slot location in set
            if self.replacement == 'LRU':
                self.replacementQueue[setIdx].pop(tag)
                self.replacementQueue[setIdx][tag] = slotIdx
        else:                                                        # MISS
            if isWrite:
                self.writeMiss += 1
            else:
                self.readMiss += 1
            slotIdx = self._setBlock(address, tag, setIdx)           # MISS - Allocate slot location in set
        return setIdx, slotIdx, offset

    cdef int _setBlock(self, int address, int tag, int setIdx):
        cdef int slotIdx, slotStart
        if self.openSetSlots[setIdx] == 0:                           # No open slots in set
            slotIdx = self._replace(tag, setIdx)
        else:                                                        # Open slots in set
            self.openSetSlots[setIdx] -= 1                           # i.e. compulsory miss
            slotIdx = self.openSetSlots[setIdx]
            self.replacementQueue[setIdx][tag] = slotIdx
        slotStart = slotIdx * self.wordsPerBlock
        self.data[setIdx, slotStart: slotStart+self.wordsPerBlock] = self.ram.getBlock(address)
        return slotIdx

    cpdef double getDouble(self, int address):
        cdef int setIdx, slotIdx, offset
        setIdx, slotIdx, offset = self._getBlock(address, isWrite=False)  # Retrieve block
        return self.data[setIdx, slotIdx * self.wordsPerBlock + offset]

    cpdef void setDouble(self, int address, double value):
        cdef int setIdx, slotIdx, offset, slotStart
        setIdx, slotIdx, offset = self._getBlock(address, isWrite=True)   # Retrieve block
        slotStart = slotIdx * self.wordsPerBlock
        self.data[setIdx, slotStart + offset] = value
        self.ram.setBlock(address, self.data[setIdx, slotStart: slotStart+self.wordsPerBlock])
