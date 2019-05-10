# ESSENTIALLY EVERY LINE WAS TAKEN FROM DIFFERENT STACK OVERFLOW OR GITHUB PAGES TOO MANY TO MENTION SPECIFICALLY.
# OF NOTE YOU MUST GO INTO THE MALTREATING FILE CREATED IN BUILD AND TURN Pool into pool (lowercase the p).
# SPECIAL THANKS TO https://www.youtube.com/watch?v=DoHWJV8iVTQ&list=PLhTjy8cBISEp6lNKUO3iwbB1DKAkRwutl&index=30
# HIS ENTIRE TUTORIAL SERIES WAS SUPER HELPFUL DURING THIS PROJECT.

# Use python setup.py build in the terminal to build the exe.

import sys
from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

# All dependencies I have had to add manually.
additional_mods = ['numpy.core._methods', 'numpy.lib.format', 'numpy.core._dtype_ctypes',
                   'matplotlib.backends.backend_tkagg', 'scipy._distributor_init', 'scipy.sparse.csgraph._validation',
                   'scipy.ndimage._ni_support', "multiprocessing", "multiprocessing.pool"]

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'includes': additional_mods, "packages": ["os"], 'include_files': ['tk86t.dll', 'tcl86t.dll'], 'excludes': 'scipy.spatial.cKDTree'}

# GUI applications require a different base on Windows (the default is for a
# console application). # COMMENT THESE TWO LINES TO GO INTO DEBUG MODE
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "PyPore",
        version = "0.1",
        description = "Porosity Extractor",
        options = {"build_exe": build_exe_options},
        executables = [Executable("PyPore.py", base=base)])