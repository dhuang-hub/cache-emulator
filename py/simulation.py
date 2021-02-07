from ram import RAM
from cache import Cache
from cpu import CPU
from numpy import arange, empty


class Simulation:
    def __init__(self, c: int, b: int, n: int, r: str, a: str, d: int, p: bool, f: int, wordSize=8):
        self.cacheSize      = c
        self.blockSize      = b
        self.nAssociativity = n
        self.replacement    = r
        self.algorithm      = a
        self.dimension      = d
        self.print          = p
        self.blockFactor    = f
        self.wordSize       = wordSize
        self.ram            = None
        self.cache          = None
        self.cpu            = None

    def printInputs(self):
        print('\nINPUTS====================================')
        print(f'Ram Size =                   {self.ram.dataSize} bytes')
        print(f'Cache Size =                 {self.cacheSize} bytes')
        print(f'Block Size =                 {self.blockSize} bytes')
        print(f'Total Blocks in Cache =      {self.cache.data.size}')
        print(f'Associativity =              {self.nAssociativity}')
        print(f'Number of Sets =             {self.cache.data.shape[0]}')
        print(f'Replacement Policy =         {self.replacement}')
        print(f'Algorithm =                  {self.algorithm}')
        print(f'MXM Blocking Factor =        {self.blockFactor}')
        print(f'Matrix or Vector dimension = {self.dimension}')

    def printResults(self):
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

    def _init_computer(self):
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
        a, b, c = arange(3 * N, dtype=int).reshape((3, -1)) * self.wordSize
        for i in range(N):
            cpu[a[i]] = i
            cpu[b[i]] = 2 * i
            cpu[c[i]] = 0

        self.printInputs()
        return a, b, c

    def _run_daxpy(self):
        a, b, c = self._init_computer()
        n = self.dimension
        cpu = self.cpu

        register0 = 3
        for i in range(n):
            register1 = cpu[a[i]]
            register2 = cpu.multDouble(register0, register1)
            register3 = cpu[b[i]]
            register4 = cpu.addDouble(register2, register3)
            cpu[c[i]] = register4

        if self.print:
            print('\nComputation result:')
            print([cpu[c[i]] for i in range(n)], end='\n\n')

    def _run_mxm(self):
        a, b, c = self._init_computer()

        # breakpoint()
        n = self.dimension
        cpu = self.cpu

        for i in range(n):
            for j in range(n):
                register0 = cpu[c[i + j*n]]
                for k in range(n):
                    register1 = cpu[a[i + k*n]]
                    register2 = cpu[b[k + j*n]]
                    register3 = cpu.multDouble(register1, register2)
                    register0 = cpu.addDouble(register0, register3)
                cpu[c[i + j*n]] = register0

        if self.print:
            d = empty(n*n)
            for i in range(n*n):
                d[i] = cpu[c[i]]
            print('\nComputation result:')
            print(d.reshape((n, n)))

    def _run_mxm_block(self):
        a, b, c = self._init_computer()
        n = self.dimension
        cpu = self.cpu
        blockFactor = self.blockFactor

        for sj in range(0, n, blockFactor):
            for si in range(0, n, blockFactor):
                for sk in range(0, n, blockFactor):
                    for i in range(si, si + blockFactor):
                        for j in range(sj, sj + blockFactor):
                            register0 = cpu[c[i + j * n]]
                            for k in range(sk, sk + blockFactor):
                                register1 = cpu[a[i + k * n]]
                                register2 = cpu[b[k + j * n]]
                                register3 = cpu.multDouble(register1, register2)
                                register0 = cpu.addDouble(register0, register3)
                            cpu[c[i + j * n]] = register0

        if self.print:
            d = empty(n*n)
            for i in range(n*n):
                d[i] = cpu[c[i]]
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
