from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QScrollArea
from PyQt5.QtCore import pyqtSignal, Qt
#from PyQt5 import Qt
#from PyQt5.QtGui import *
from datanodes.core.node_socket import *


class DataLineEdit(QLineEdit):
    def __init__(self, name, node):
        super().__init__(name)
        self.node     = node

    def setTitle(self):
        self.node.title             = self.text()
        self.node.properties.title  = self.text()

        

class NodeProperties(QScrollArea, Serializer):
    changed    = pyqtSignal()
    outchanged = pyqtSignal()

    def __init__(self, node, parent=None):
        self.node = node
        super().__init__(parent)
        
        self.title_label = None
        self.title       = ""
        self.title_widget= None
        self.i       = 0
        self.initUI()
        self.setMinimumHeight(150)
    
    def setTitle(self):
        self.title_label = QLabel("Title ", self)        
        self.title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.title_label.setStyleSheet("margin-bottom: 15px; margin-top:5px;")
        
        self.title_widget = DataLineEdit(self.title, self.node)
        self.title_widget.setAlignment(Qt.AlignLeft)
        self.title_widget.textChanged.connect(self.title_widget.setTitle)
        self.title_widget.setStyleSheet("margin-bottom: 15px; margin-top:5px;")
        
        self.layout.addWidget(self.title_label, self.i, 0)
        self.layout.addWidget(self.title_widget, self.i, 1)
        self.i += 1

    def clearProperties(self):
        self.i = 0
        self.c = 0
        if self.layout is not None:
            for i in reversed(range(self.layout.count())):
                self.layout.itemAt(i).widget().setParent(None)

    def resetProperties(self):
        self.clearProperties()
        self.setTitle()

    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10,5,10,5)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.scroll_widget = QWidget(self)
        self.scroll_widget.setLayout(self.layout)
        self.setWidget(self.scroll_widget)
        
        self.setTitle()

    def emitChanged(self):
        self.changed.emit()
        self.node.title = self.title_widget.text()
        self.title = self.title_widget.text()

    def serialize(self):
        return OrderedDict([
            ('id' ,    self.id),
            ('title',  self.title),
            ('width',  self.node.grNode.width),
            ('height', self.node.grNode.height),
        ])
        
    def deserialize(self, data, hashmap=[]):
        self.id = data['id']
        hashmap[data['id']] = self
        self.node.grNode.height = data['height']
        self.node.grNode.width  = data['width']
        self.node.title         = data['title']
        self.title              = data['title']
        self.node.content.updateSize()
        self.title_widget.setText(data['title'])
        return True
