from simulation import Simulation
import numpy as np

default_params = {
    'c': 65536,
    'b': 64,
    'n': 2, 
    'r': 'LRU',
    'a': 'mxm_block',
    'd': 480,
    'p': True,
    'f': 32
}


def init_test():
    for alg in ['daxpy', 'mxm']:
        for rep in ['LRU', 'FIFO', 'random']:
            test_params = default_params.copy()
            test_params['a'] = alg
            test_params['r'] = rep
            test_params['d'] = 100
            test_params['f'] = 5

            sim = Simulation(**test_params)

            sim._init_computer()
            cache = sim.cache
            cpu = sim.cpu
            n = sim.dimension
            wordSize = sim.wordSize

            if sim.algorithm == 'daxpy':
                N = n
            else:
                N = n * n

            a = [cpu[i*wordSize] for i in range(N)]
            b = [cpu[i*wordSize] for i in range(N, 2*N)]
            c = [cpu[i*wordSize] for i in range(2*N, 3*N)]

            A = np.arange(N, dtype=int)
            B = 2 * A
            C = np.zeros(N, dtype=int)

            try:
                assert A.tolist() == a
                assert B.tolist() == b
                assert C.tolist() == c
            except AssertionError:
                breakpoint()


def daxpy_test():
    for nAss in [1, 2]:
        for rep in ['LRU', 'FIFO', 'random']:
            for dim in [2**6, 2**8, 2**10]:
                test_params = default_params.copy()
                test_params['c'] = 8192
                test_params['a'] = 'daxpy'
                test_params['r'] = rep
                test_params['d'] = dim
                test_params['n'] = nAss
                test_params['p'] = False

                sim = Simulation(**test_params)
                sim.run()

                cpu = sim.cpu
                wordSize = sim.wordSize

                N = dim
                a = [cpu[i*wordSize] for i in range(N)]
                b = [cpu[i*wordSize] for i in range(N, 2*N)]
                c = [cpu[i*wordSize] for i in range(2*N, 3*N)]

                A = np.arange(N, dtype=int)
                B = 2 * A
                C = 3*A + B

                try:
                    assert A.tolist() == a
                    assert B.tolist() == b
                    assert C.tolist() == c
                except AssertionError:
                    breakpoint()


def mxm_test():
    for nAss in [1, 2]:
        for rep in ['LRU', 'FIFO', 'random']:
            for dim in [2**6, 2**7]:
                test_params = default_params.copy()
                test_params['a'] = 'mxm'
                test_params['r'] = rep
                test_params['d'] = dim
                test_params['n'] = nAss
                test_params['p'] = False

                sim = Simulation(**test_params)
                sim.run()

                cpu = sim.cpu
                wordSize = sim.wordSize

                N = dim*dim
                a = [cpu[i*wordSize] for i in range(N)]
                b = [cpu[i*wordSize] for i in range(N, 2*N)]
                c = [cpu[i*wordSize] for i in range(2*N, 3*N)]

                A = np.arange(N, dtype=int)
                B = 2 * A
                C = (A.reshape((dim, dim)) @ B.reshape((dim, dim))).reshape(-1)

                try:
                    assert A.tolist() == a
                    assert B.tolist() == b
                    assert C.tolist() == c
                except AssertionError:
                    breakpoint()

def mxm_block_test():
    for nAss in [1, 2]:
        for rep in ['LRU', 'FIFO', 'random']:
            for dim in [2**6, 2**7]:
                test_params = default_params.copy()
                test_params['r'] = rep
                test_params['d'] = dim
                test_params['n'] = nAss
                test_params['p'] = False

                sim = Simulation(**test_params)
                sim.run()

                cpu = sim.cpu
                wordSize = sim.wordSize

                N = dim*dim
                a = [cpu[i*wordSize] for i in range(N)]
                b = [cpu[i*wordSize] for i in range(N, 2*N)]
                c = [cpu[i*wordSize] for i in range(2*N, 3*N)]

                A = np.arange(N, dtype=int)
                B = 2 * A
                C = (A.reshape((dim, dim)) @ B.reshape((dim, dim))).reshape(-1)

                try:
                    assert A.tolist() == a
                    assert B.tolist() == b
                    assert C.tolist() == c
                except AssertionError:
                    breakpoint()



if __name__ == '__main__':
    # init_test()
    daxpy_test()
    mxm_test()
    mxm_block_test()