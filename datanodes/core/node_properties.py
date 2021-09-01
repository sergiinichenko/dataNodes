from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datanodes.core.node_socket import *


class DataLineEdit(QLineEdit):
    def __init__(self, name, node):
        super().__init__(name)
        self.node     = node

    def setTitle(self):
        self.node.title = self.text()

        

class NodeProperties(QWidget, Serializer):
    changed    = pyqtSignal()
    outchanged = pyqtSignal()

    def __init__(self, node, parent=None):
        self.node = node
        super().__init__(parent)
        
        self.title_label = None
        self.title       = None
        self.i       = 0
        self.initUI()
        self.setMinimumHeight(150)

    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)

        self.title_label = QLabel("Title ", self)        
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        
        self.title = DataLineEdit(self.node.title, self.node)
        self.title.setAlignment(Qt.AlignLeft)
        self.title.textChanged.connect(self.title.setTitle)
        
        self.layout.addWidget(self.title_label, self.i, 0)
        self.layout.addWidget(self.title, self.i, 1)
        self.i += 1

    def emitChanged(self):
        self.changed.emit()
        self.node.title = self.title.text()

    def serialize(self):
        return OrderedDict([
            ('id' ,   self.id),
            ('title', self.title.text()),
            ('width',  self.node.grNode.width),
            ('height', self.node.grNode.height),
        ])
        
    def deserialize(self, data, hashmap=[]):
        self.id = data['id']
        hashmap[data['id']] = self
        self.node.grNode.height = data['height']
        self.node.grNode.width  = data['width']
        self.node.title         = data['title']
        self.node.content.updateSize()
        return True
