import sys
from PyQt5.QtWidgets import *
from datanodes.core.main_window import MainWindow
from datanodes.core.utils import *
import os, inspect
if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MainWindow()
   
    sys.exit(app.exec_())
