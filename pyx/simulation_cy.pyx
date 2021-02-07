from cpu_cy import CPU
from cache_cy import Cache
from ram_cy import RAM
import numpy as np
cimport numpy as np
# cimport cython


cdef class Simulation:
    cdef public object ram, cache, cpu
    cdef readonly int cacheSize, blockSize, nAssociativity, dimension, blockFactor, wordSize
    cdef readonly bint print_
    cdef readonly str replacement, algorithm

    def __init__(self, c: int, b: int, n: int, r: str, a: str, d: int, p: bool, f: int, wordSize=8):
        self.cacheSize      = c
        self.blockSize      = b
        self.nAssociativity = n
        self.replacement    = r
        self.algorithm      = a
        self.dimension      = d
        self.print_         = p
        self.blockFactor    = f
        self.wordSize       = wordSize
        self.ram            = None
        self.cache          = None
        self.cpu            = None

    cpdef void printInputs(self):
        cdef int cacheBits, blockBits, setBits
        cacheBits = self.cache.cacheBits
        blockBits = self.cache.blockBits
        setBits   = self.cache.setBits
        print('\nINPUTS====================================')
        print(f'Ram Size =                   {self.ram.dataSize} bytes')
        print(f'Cache Size =                 {self.cacheSize} bytes')
        print(f'Block Size =                 {self.blockSize} bytes')
        print(f'Total Blocks in Cache =      {1 << (cacheBits-blockBits)}')
        print(f'Associativity =              {self.nAssociativity}')
        print(f'Number of Sets =             {1 << setBits}')
        print(f'Replacement Policy =         {self.replacement}')
        print(f'Algorithm =                  {self.algorithm}')
        print(f'MXM Blocking Factor =        {self.blockFactor}')
        print(f'Matrix or Vector dimension = {self.dimension}')

    cpdef void printResults(self):
        readHit    = self.cache.readHit
        readMiss   = self.cache.readMiss
        writeHit   = self.cache.writeHit
        writeMiss  = self.cache.writeMiss
        readMissR  = readMiss / (readHit+readMiss)
        writeMissR = writeMiss / (writeHit+writeMiss)
        print('\nRESULTS===================================')
        print(f'Instruction count: {self.cpu.instructionCount}')
        print(f'Read hits:         {readHit}')
        print(f'Read misses:       {readMiss}')
        print(f'Read miss rate:    {readMissR:.2%}')
        print(f'Write hits:        {writeHit}')
        print(f'Write misses:      {writeMiss}')
        print(f'Write miss rate:   {writeMissR:.2%}')

    cpdef _init_computer(self):
        cdef int n, N, i
        cdef np.ndarray[np.uint32_t, ndim=1] a, b, c
        n = self.dimension
        if self.algorithm == 'daxpy':
            N = n
        else:
            N = n * n
        dataSize = 3 * N * self.wordSize
        self.ram = RAM(dataSize, self.blockSize, self.wordSize)
        self.cache = Cache(self.ram, self.cacheSize, self.blockSize, self.nAssociativity,
                           self.replacement, self.wordSize)
        self.cpu = CPU(self.cache)
        cpu = self.cpu
        a, b, c = np.arange(3 * N, dtype='u4').reshape((3, -1)) * self.wordSize
        for i in range(N):
            cpu.storeDouble(a[i], i)
            cpu.storeDouble(b[i], 2 * i)
            cpu.storeDouble(c[i], 0)
        self.printInputs()
        return a, b, c

    cdef void _run_daxpy(self):
        cdef int n, i
        cdef np.ndarray[np.uint32_t, ndim=1] a, b, c
        cdef double register0, register1, register2, register3, register4
        a, b, c = self._init_computer()
        n = self.dimension
        cpu = self.cpu
        register0 = 3
        for i in range(n):
            register1 = cpu.loadDouble(a[i])
            register2 = cpu.multDouble(register0, register1)
            register3 = cpu.loadDouble(b[i])
            register4 = cpu.addDouble(register2, register3)
            cpu.storeDouble(c[i], register4)
        if self.print_:
            print('\nComputation result:')
            print([cpu.loadDouble(c[i]) for i in range(n)])

    cdef void _run_mxm(self):
        cdef int n, i, j, k
        cdef np.ndarray[np.uint32_t, ndim=1] a, b, c
        cdef double register0, register1, register2, register3
        a, b, c = self._init_computer()
        n = self.dimension
        cpu = self.cpu
        for i in range(n):
            for j in range(n):
                register0 = cpu.loadDouble(c[i + j*n])
                for k in range(n):
                    register1 = cpu.loadDouble(a[i + k*n])
                    register2 = cpu.loadDouble(b[k + j*n])
                    register3 = cpu.multDouble(register1, register2)
                    register0 = cpu.addDouble(register0, register3)
                cpu.storeDouble(c[i + j*n], register0)
        if self.print_:
            d = np.empty(n*n)
            for i in range(n*n):
                d[i] = cpu.loadDouble(c[i])
            print('\nComputation result:')
            print(d.reshape((n, n)))

    cdef void _run_mxm_block(self):
        cdef int n, blockFactor, i, si, j, sj, k, sk
        cdef np.ndarray[np.uint32_t, ndim=1] a, b, c
        cdef double register0, register1, register2, register3
        a, b, c = self._init_computer()
        n = self.dimension
        cpu = self.cpu
        blockFactor = self.blockFactor
        for sj in range(0, n, blockFactor):
            for si in range(0, n, blockFactor):
                for sk in range(0, n, blockFactor):
                    for i in range(si, si + blockFactor):
                        for j in range(sj, sj + blockFactor):
                            register0 = cpu.loadDouble(c[i + j * n])
                            for k in range(sk, sk + blockFactor):
                                register1 = cpu.loadDouble(a[i + k * n])
                                register2 = cpu.loadDouble(b[k + j * n])
                                register3 = cpu.multDouble(register1, register2)
                                register0 = cpu.addDouble(register0, register3)
                            cpu.storeDouble(c[i + j * n], register0)
        if self.print_:
            d = np.empty(n*n)
            for i in range(n*n):
                d[i] = cpu.loadDouble(c[i])
            print('\nComputation result:')
            print(d.reshape((n, n)))

    def run(self):
        if self.algorithm == 'daxpy':
            self._run_daxpy()
        elif self.algorithm == 'mxm':
            self._run_mxm()
        elif self.algorithm == 'mxm_block':
            assert self.dimension % self.blockFactor is 0
            self._run_mxm_block()
        else:
            raise ValueError

        self.printResults()
