"""
To run Cython compilation yourself, invoke the following command
from the current directory 'pyx'.

python setup.py build_ext --inplace --force

For each of the compiled implementation files, three new files
are generated, *.c, *.so/*.pyd, *.html. Python scripts can proceed
to import compiled modules from the local directory that contain
the *.so file. Optionally, one can choose to manually compile the
*.c file. The *.html file is an annotated scan of the compile
code, hinting at Python / C interactions (slowness & overhead).
Script at the bottom automatically moves generated *.c and *.html
files to respective directories: 'cy_cfiles' and 'cy_annotations'.

Compilation may kick out warnings.

I encountered a Mac compilation issue, addressed in comments below.
"""


# from setuptools import setup
from distutils.core import setup
from Cython.Build import cythonize
import Cython.Compiler.Options as Options
import numpy as np
import shutil
import glob

Options.annotate = True

# Mac Users Compilation Issue:
# fatal error: 'numpy/arrayobject.h' file not found
# include "numpy/arrayobject.h"
#
# Quick-Fix Solution:
# Run the below export in the shell environment with
# the printed numpy path, replacing the bracketed part
# export CFLAGS=-I{np.get_include()}

print(np.get_include())

setup(
    name='Cache Simulation',
    ext_modules=cythonize('cpu_cy.pyx',
        include_path=[np.get_include()]),
    zip_safe=False,
)

setup(
    name='Cache Simulation',
    ext_modules=cythonize('ram_cy.pyx',
        include_path=[np.get_include()]),
    zip_safe=False,
)

setup(
    name='Cache Simulation',
    ext_modules=cythonize('simulation_cy.pyx',
        include_path=[np.get_include()]),
    zip_safe=False,
)

setup(
    name='Cache Simulation',
    ext_modules=cythonize('cache_cy.pyx',
        include_path=[np.get_include()]),
    zip_safe=False,
)

for srcfile in glob.glob('*.c'):
    shutil.move(srcfile, f'./cy_cfiles/{srcfile}')

for srcfile in glob.glob('*.html'):
    shutil.move(srcfile, f'./cy_annotations/{srcfile}')

for srcfile in glob.glob('*.so'):
    shutil.move(srcfile, f'../{srcfile}')

for srcfile in glob.glob('*.pyd'):
    shutil.move(srcfile, f'../{srcfile}')
