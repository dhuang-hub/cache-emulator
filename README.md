# Project 1: Cython Cache Simulator
#### By David Huang


## Read Version 1, Run Version 2
I have two implementations that are largely the same, but one
is compiled for speed optimization (Version 2). Version 1 is easier
to read without the static type declarations. My implementations
**must be run on Python versions of at least 3.7**!

Note: Beginning with Python 3.7, Python dictionaries order items by entry time
by default.

TL;DR Scroll to bottom.


## Version 1: Python 3
#### Environment Requirements
- Python 3.7+
- numpy
- And respective dependencies

#### Running Code
I first approached this project with a completely Pythonic build.
 All of my work for the pure python build is stored away in the
`py` directory. It works as expected, invoked with the following
command ***from within the directory*** `py`:

`python cache-sim.py [parameter options]`

I have a test script, `test.py` that runs through a gamut
of many configurations, checking for computation correctness against
an externally computed result via numpy. The test script can be
invoked ***from within the directory*** `py` with the following
command: 

`python test.py`


## Version 2: Cythonization
#### Environment Requirements
- Python 3.7+
- numpy
- cython  
- And respective dependencies

#### Compilation
In search of speed, I know that I shouldn't be using Python.
However, I set out to improve upon Version 1 with Cython compilation.
This mostly involved introducing static typing to the source code
at the cost of verbosity and readability. All the implementation
code for Cython compilation are stored in the `pyx` directory.
Cython compilation happens in two stages:
- A .pyx file is compiled by Cython to a .c file.
- The .c file is compiled by a C compiler to a .so file (or a .pyd
  file on Windows)

To compile the code yourself, run the following command
***from within the directory*** `pyx`:

`python setup.py build_ext --inplace --force`

The `setup.py` script will compile the `*.pyx` implementation code
and generate three additional files of the forms `*.html`, `*.c`, and
`*.so`/`*.pyd`. The `setup.py` script will tidy up placement and
sequester `*.html` and `*.c` files to the respective directories
`pyx/cy_annotations` and `pyx/cy_cfiles`. The `*.html` files are
annotations the compiler makes to hint at Python/C interactions
(i.e. slowness and overhead). One may manually compile the generated
`*.c` files themselves (I have not tried, but one can do this to
totally bypass cython with the `*.c` files I generated). The setup
script will also move the compiled `*.so`/`*.pyd` files to the
top-level directory level where this `README.md` sits.

Note: I've included `darwin-compile-files.zip` of importable modules,
compiled on my Macbook machine. Mac users should be able to unzip
and run the files with the instructions detailed below (no
re-compilation required).

Note: For Mac users (like myself), Cython compilation may kick out
a known error that is supposedly patched, but not yet distributed.
There is a quick fix for this, and I've detailed it in the comments
of the `pyx/setup.py` file.


#### Running Code
***From within the top-level directory*** (i.e. where the `README.md`
file sits), one can run the simulation with the usual command:

`python cache-sim.py [parameter options]`

Note: The `cache-sim.py ` located in directory `py` versus the one at
the top-level are nearly identical, except the top-level script
imports the Cython compiled source code.

For correctness, I have a `test_cy.py` script (runtime: ~2-3 mins).

`python test_cy.py`

## Speed Benchmarks on my MacBook
Running defaults, except for `dimension = 128`. No printing.
- Python: ~25 secs
- Cython: ~3-4 secs

Running defaults. No printing.
- Python: ~1700 secs
- Cython: ~150 secs


## Correctness
#### daxpy

`python cache-sim.py -d 9 -a daxpy -p`

```
Computation result:
[0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]
```


#### mxm / mxm_block

`python cache-sim.py -d 9 -a mxm -p`

`python cache-sim.py -d 9 -a mxm_block -f 3 -p`

```
Computation result:
[[ 3672.  3744.  3816.  3888.  3960.  4032.  4104.  4176.  4248.]
 [ 9504.  9738.  9972. 10206. 10440. 10674. 10908. 11142. 11376.]
 [15336. 15732. 16128. 16524. 16920. 17316. 17712. 18108. 18504.]
 [21168. 21726. 22284. 22842. 23400. 23958. 24516. 25074. 25632.]
 [27000. 27720. 28440. 29160. 29880. 30600. 31320. 32040. 32760.]
 [32832. 33714. 34596. 35478. 36360. 37242. 38124. 39006. 39888.]
 [38664. 39708. 40752. 41796. 42840. 43884. 44928. 45972. 47016.]
 [44496. 45702. 46908. 48114. 49320. 50526. 51732. 52938. 54144.]
 [50328. 51696. 53064. 54432. 55800. 57168. 58536. 59904. 61272.]]

```

Note: My `mxm_block` implementation will throw an assertion error
if the dimension is not divisible by the blocking factor.

#### Test Scripts
`python py/test.py`

`python test_cy.py`


# TL;DR
1. Compile: `python pyx/setup.py`

2. Run: `python cache-sim.py [parameter options]`