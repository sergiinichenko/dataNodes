from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class NodeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stylesheet_filename = "qss/nodestyle.qss"
        self.loadStyleSheet(self.stylesheet_filename)

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.layout.addWidget(QTextEdit("foo"))

    def loadStyleSheet(self, filename):
        print("STYLE loading : ", filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)

        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8',))