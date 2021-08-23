from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datanodes.core.utils import *
from datanodes.core.main_conf import *


class PropertiesDock(QDockWidget):
    def __init__(self, name="Properties", parent = None):
        super().__init__(name, parent=parent)

        self.initUI()

    def initUI(self):
        self.setFloating(False)
        self.hide()
