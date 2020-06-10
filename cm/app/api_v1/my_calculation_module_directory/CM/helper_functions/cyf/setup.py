from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy
import os
import re
import sys

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__))))

extra_compile_args = []
extra_link_args = []
if os.name == 'posix':
    extra_compile_args = ['-fopenmp', '-O3', '-ffast-math', '-march=native']
    extra_link_args = ['-fopenmp']

def get_extensions():
    extensions = []
    for root, subFolders, files in os.walk('.'):
        for _f in files:
            if _f.endswith('.pyx'):
                f = os.path.join(root, _f)
                sources = [f]

                name = re.sub(r'(.pyx)$', '', f)\
                        .replace('./', '')\
                        .replace('/', '.')\
                        .replace('\\', '.')\
                        .replace('..', '')

                extensions.append(
                        Extension(name, sources, extra_compile_args=extra_compile_args, extra_link_args=extra_link_args))
    return extensions

setup(
    name = 'CM compiled',
    ext_modules = cythonize(get_extensions()),
    include_dirs=[numpy.get_include()] , compiler_directives={'language_level' : sys.version_info[0]}
)
