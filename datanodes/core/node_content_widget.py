from datanodes.core.node_serializer import Serializer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from collections import OrderedDict

DEBUG = False

class NodeWidget(QWidget, Serializer):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.layout.addWidget(QTextEdit("foo"))


    def serialize(self):
        return OrderedDict([
            ('id' , self.id),
            ('content', "")
        ])
        
    def deserialize(self, data, hashmap=[]):
        #print("Deserialization of the data", data)
        return False