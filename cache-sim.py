import argparse
# from simulation import Simulation
from time import time
from simulation_cy import Simulation

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', default=65536, help='The size of the cache in bytes (default: 65,536)', type=int)
    parser.add_argument('-b', default=64, help='The size of a data block in bytes (default: 64)', type=int)
    parser.add_argument('-n', default=2, help='The n-way associativity of the cache. -n 1 is a direct-mapped cache. (default: 2)', type=int)
    parser.add_argument('-r', default='LRU', help='The replacement policy. Can be random, FIFO, or LRU. (default: LRU)', type=str)
    parser.add_argument('-a', default='mxm_block', help='The algorithm to simulate. Can be daxpy (daxpy product), mxm (matrix-matrix multiplication), mxm block (mxm with blocking). (default: mxm block).', type=str)
    parser.add_argument('-d', default=480, help='The dimension of the algorithmic matrix (or vector) operation. -d 100 would result in a 100 × 100 matrix-matrix multiplication. (default: 480)', type=int)
    parser.add_argument('-p', action='store_true', help='Enables printing of the resulting “solution” matrix product or daxpy vector after the emulation is complete. Elements should be read in emulation mode (e.g., using your loadDouble method), so as to assess if the emulator actually produced the correct solution.')
    parser.add_argument('-f', default=32, help='The blocking factor for use when using the blocked matrix multiplication algorithm. (default: 32)', type=int)
    kwargs = vars(parser.parse_args())

    S = Simulation(**kwargs)
    stime = time()
    S.run()
    etime = time()
    print(f'Runtime:           {etime-stime:.2f} secs')

if __name__ == '__main__':
    main()