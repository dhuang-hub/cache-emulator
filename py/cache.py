from math import log2
from numpy import full, zeros
from random import randrange


class Cache:
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
        self.openSetSlots     = full(1 << setBits, nAssociativity, dtype='i4')
        self.data             = zeros((1 << setBits, nAssociativity * wordsPerBlock))
        self.replacement      = replacement if nAssociativity > 1 else None
        self.replacementQueue = [dict() for _ in range(1 << setBits)]
        self.replaceMethod    = None
        if self.replacement == 'random':
            self.replaceMethod = self._replaceRandom
        else:
            self.replaceMethod = self._replaceQueue

        # event log
        self.readHit   = 0
        self.readMiss  = 0
        self.writeHit  = 0
        self.writeMiss = 0

    def parseAddress(self, address):
        offset   = (address & self.blockMask) >> self.wordBits
        address  = address >> self.blockBits
        tag      = address >> self.setBits
        setIdx   = address & self.setMask
        return tag, setIdx, offset

    def _replaceQueue(self, tag, setIdx):
        # assert tag not in self.replacementQueue[setIdx]
        # assert len(self.replacementQueue[setIdx]) == self.nAssociativity
        lruTag = next(iter(self.replacementQueue[setIdx]))
        slotIdx = self.replacementQueue[setIdx].pop(lruTag)
        self.replacementQueue[setIdx][tag] = slotIdx
        return slotIdx

    def _replaceRandom(self, tag, setIdx):
        # assert tag not in self.replacementQueue[setIdx]
        # assert len(self.replacementQueue[setIdx]) == self.nAssociativity
        randTag = list(self.replacementQueue[setIdx])[randrange(self.nAssociativity)]
        slotIdx = self.replacementQueue[setIdx].pop(randTag)
        self.replacementQueue[setIdx][tag] = slotIdx
        return slotIdx

    def _getBlock(self, address, isWrite):
        tag, setIdx, offset = self.parseAddress(address)
        if tag in self.replacementQueue[setIdx]:                        # HIT
            if isWrite:
                self.writeHit += 1
            else:
                self.readHit += 1
            slotIdx = self.replacementQueue[setIdx][tag]
            if self.replacement == 'LRU':                               # update access time
                self.replacementQueue[setIdx].pop(tag)
                self.replacementQueue[setIdx][tag] = slotIdx
        else:                                                           # MISS
            if isWrite:
                self.writeMiss += 1
            else:
                self.readMiss += 1
            slotIdx = self._setBlock(address, tag, setIdx)
        return setIdx, slotIdx, offset

    def _setBlock(self, address, tag, setIdx):
        if self.openSetSlots[setIdx] == 0:  # no open slots
            slotIdx = self.replaceMethod(tag, setIdx)
        else:                               # open slots
            self.openSetSlots[setIdx] -= 1  # decrement open slot count
            slotIdx = self.openSetSlots[setIdx]
            self.replacementQueue[setIdx][tag] = slotIdx
        slotStart = slotIdx * self.wordsPerBlock
        self.data[setIdx, slotStart: slotStart+self.wordsPerBlock] = self.ram[address]
        return slotIdx

    # getDouble
    def __getitem__(self, address):
        setIdx, slotIdx, offset = self._getBlock(address, isWrite=False)
        return self.data[setIdx, slotIdx * self.wordsPerBlock + offset]

    # setDouble
    def __setitem__(self, address, value):
        setIdx, slotIdx, offset = self._getBlock(address, isWrite=True)
        slotStart = slotIdx * self.wordsPerBlock
        self.data[setIdx, slotStart + offset] = value
        self.ram[address] = self.data[setIdx, slotStart: slotStart+self.wordsPerBlock]
