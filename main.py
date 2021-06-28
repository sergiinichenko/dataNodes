import sys, os
from PyQt5.QtWidgets import *
sys.path.insert(0, os.path.join( os.path.dirname(__file__), '..', '..'))

from datanodes.core.main_window import MainWindow
from datanodes.core.node_window import NodeWindow
from datanodes.core.utils import *
import os, inspect
if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MainWindow()
   
    sys.exit(app.exec_())
