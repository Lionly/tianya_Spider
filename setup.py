# setup.py 
from distutils.core import setup
import py2exe

# setup(service=["WindowsService"], zipfile=None)
# setup(windows=["tk.py"], zipfile=None)
setup(console=["tk.py"], zipfile=None)