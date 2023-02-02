
#__all__ = ['inputs', 'math', 'outputs']


from os.path import dirname, basename, isfile, join, abspath
import glob
import sys

from datanodes.nodes.array import *
from datanodes.nodes.comment import *
from datanodes.nodes.datanode import *
from datanodes.nodes.filter import *
from datanodes.nodes.graphics import *
from datanodes.nodes.input_file import *
from datanodes.nodes.inputs import *
from datanodes.nodes.math import *
from datanodes.nodes.output_file import *
from datanodes.nodes.outputs import *
from datanodes.nodes.process import *
from datanodes.nodes.statistics import *
"""
def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    return join(base_path, relative_path)


#modules = resource_path(glob.glob(join(dirname(__file__), "*.py")))
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
print("__all__", __all__)

print(" ---- content ----", glob.glob(join(dirname(__file__), "*")))
print(" ---- content ----", join(resource_path("datanodes\\nodes"), "*.py"))#dirname(__file__))
"""