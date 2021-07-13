from datanodes.graphics.graphics_view import MODE_DRAG_RESIZE, MODE_NONE
from datanodes.core.utils import dumpException
from datanodes.core.node_node import Node
from datanodes.core.node_content_widget import NodeContentWidget
from datanodes.graphics.graphics_node import GraphicsNode
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datanodes.core.node_socket import *
import os
import pandas as pd
import numpy as np

DEBUG = False

class DataGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 100.0
    
    def initAssets(self):
        super().initAssets()
        path = os.path.dirname(os.path.abspath(__file__))
        self.icons    = QImage(os.path.join(path, "../icons/status_icons.png"))
        self.drag_img = QImage(os.path.join(path, "../icons/drag.png"))
    
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
        
        if self.node.isMute():
            path_mute = QPainterPath()
            path_mute.setFillRule(Qt.WindingFill)
            path_mute.addRoundedRect(0,0,self.width, self.height,
                    self.border_radius, self.border_radius)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(117, 90, 88, 128)))
            painter.drawPath(path_mute.simplified())

    def itemChange(self, change, value):
        if self.isSelected() and not self.is_selected:
            self.is_selected = True
        else:
            self.is_selected = False
        return super().itemChange(change, value)

class DataContent(NodeContentWidget):
    changed = pyqtSignal()
    def initUI(self):
        pass


class DataNode(Node):
    op_code  = 0
    op_title = "Base node"
    icon     = ""

    def __init__(self, scene, inputs=[1,1], outputs=[2,2], innames=None, outnames=None):
        super().__init__(scene, self.__class__.op_title, inputs, outputs, innames, outnames)

        #self.value = None
        self.e     = None
        self.type  = "float"
        self.recalculate = False
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
            #return self.value
            return True

        try:
            if self.isMute():
                if len(self.getInputs()) > 0:
                    value = self.getInput(0).value
                    type  = self.getInput(0).type
                else:
                    value = 0.0
                    type  = "float"
                
                if len(self.getOutputs()) > 0:
                    for output in self.getOutput():
                        output.value = value
                        output.type  = inputtype
                return True


            if self.evalImplementation():
                self.setDirty(False)
                self.setInvalid(False)
                self.setDescendentsInvalid(False)
                self.setDescendentsDirty()
                self.evalChildren()
                return True
            else: 
                self.setInvalid(True)
                self.setDescendentsInvalid(True)
                self.setDescendentsDirty(False)
                self.grNode.setToolTip(str(self.e))
                return False

        except Exception as e : 
            self.setInvalid()
            dumpException(e)
            self.grNode.setToolTip(str(e))


    def reEvaluate(self):
        self.setDirty()
        self.eval()

    def onInputChanged(self, new_edge):
        if DEBUG : print("DATANODE : oninputChanged")
        self.setDirty()
        if DEBUG : print("DATANODE : to run the eval")
        self.eval()
        if DEBUG : print("DATANODE : the eval is done")


    def serialize(self):
        res = super().serialize()
        res['op_code']  = self.__class__.op_code
        res['op_title'] = self.__class__.op_title  
        return res      

    def deserialize(self, data, hashmap=[], restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        return True


class ResizebleDataNode(DataGraphicsNode):
    def __init__(self, node, parent=None):
        super().__init__(node, parent)
        #self.startSize = self.size()
        self.mode = MODE_NONE


    def adjustSize(self):
        super().adjustSize()

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos()) - self.scenePos()
        self.init_pos  = self.mapToScene(event.pos())
        self.init_size = self.width, self.height
        self.content_init_size = self.content.size()

        x, y = pos.x(), pos.y()
        if x < self.width and x > (self.width - 20) and y < self.height and y > (self.height - 20):
            self.mode = MODE_DRAG_RESIZE
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == MODE_DRAG_RESIZE:
            scale = self.mapToScene(event.pos()) - self.init_pos
            self.width  = self.init_size[0] + scale.x()
            self.height = self.init_size[1] + scale.y()
            self.update()
            x, y = self.content_init_size.width() + scale.x(), self.content_init_size.height() + scale.y()
            self.content.resize(x, y)
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mode == MODE_DRAG_RESIZE:
            self.mode = MODE_NONE
            super().mouseReleaseEvent(event)
            return

        super().mouseReleaseEvent(event)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        if self.is_selected:
            drag_size = 24-2
            x = self.width - drag_size
            y = self.height - drag_size
            painter.drawImage(
                QRectF(x, y, drag_size, drag_size),
                self.drag_img,
                QRectF(0.0, 0.0, drag_size, drag_size)
                )

