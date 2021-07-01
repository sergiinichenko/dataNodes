from datanodes.core.utils import dumpException
from datanodes.core.node_node import Node
from datanodes.core.node_content_widget import NodeContentWidget
from datanodes.graphics.graphics_node import GraphicsNode
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datanodes.core.node_socket import *
import os


class DataGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 100.0
    
    def initAssets(self):
        super().initAssets()
        path = os.path.dirname(os.path.abspath(__file__))
        self.icons = QImage(os.path.join(path, "../icons/status_icons.png"))
    
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0
        if self.node.isDirty()   : offset =  0.0
        if self.node.isInvalid() : offset = 48.0

        painter.drawImage(
            QRectF(-10.0, -10.0, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0.0, 24.0, 24.0)
            )

class DataContent(NodeContentWidget):
    changed = pyqtSignal()
    def initUI(self):
        pass


class DataNode(Node):
    op_code  = 0
    op_title = "Base node"
    icon     = ""

    def __init__(self, scene, inputs=[1,1], outputs=[2,2]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

        self.value = None
        self.e     = None
        self.type  = "float"
        # Mark all nodes dirty by default before it is connected to anything
        self.setDirty()


    def initInnerClasses(self):
        self.content = DataContent(self)
        self.grNode  = DataGraphicsNode(self)
        self.content.changed.connect(self.eval())


    def initSettings(self):
        super().initSettings()
        self.socket_spacing = 24.0
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER


    def evalImplementation(self):
        return 123


    def eval(self):
        if not self.isDirty() and not self.isInvalid() and not self.recalculate:
            return self.value

        try:
            if self.evalImplementation():
                self.setDirty(False)
                self.setInvalid(False)
                self.setDescendentsInvalid(False)
                self.setDescendentsDirty()
                self.evalChildren()
                return self.value
            else: 
                self.setInvalid(True)
                self.setDescendentsInvalid(True)
                self.setDescendentsDirty(False)
                self.grNode.setToolTip(str(self.e))
                return 0

        except Exception as e : 
            self.setInvalid()
            dumpException(e)
            self.grNode.setToolTip(str(e))


    def reEvaluate(self):
        self.setDirty()
        self.eval()

    def onInputChanged(self, new_edge):
        self.setDirty()
        self.eval()


    def serialize(self):
        res = super().serialize()
        res['op_code']  = self.__class__.op_code
        res['op_title'] = self.__class__.op_title  
        return res      

    def deserialize(self, data, hashmap=[], restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialized base data node {0}".format(self.__class__.__name__,), "res: ", res)