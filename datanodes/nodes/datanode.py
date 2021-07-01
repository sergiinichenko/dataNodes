from datanodes.core.node_node import Node
from datanodes.core.node_content_widget import NodeContentWidget
from datanodes.graphics.graphics_node import GraphicsNode
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datanodes.core.node_socket import *


class DataGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 100.0

class DataContent(NodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)


class DataNode(Node):
    op_code  = 0
    op_title = "Base node"
    icon     = ""

    def __init__(self, scene, inputs=[1,1], outputs=[2,2]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

    def initInnerClasses(self):
        self.content = DataContent(self)
        self.grNode  = DataGraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.socket_spacing = 24.0
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def serialize(self):
        res = super().serialize()
        res['op_code']  = self.__class__.op_code
        res['op_title'] = self.__class__.op_title  
        return res      

    def deserialize(self, data, hashmap=[], restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialized base data node {0}".format(self.__class__.__name__,), "res: ", res)