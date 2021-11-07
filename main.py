import sys, os
from PyQt5.QtWidgets import *
sys.path.insert(0, os.path.join( os.path.dirname(__file__), '..', '..'))
import faulthandler 
faulthandler.enable()

from datanodes.core.main_window import MainWindow
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MainWindow()
    sys.exit(app.exec_())
