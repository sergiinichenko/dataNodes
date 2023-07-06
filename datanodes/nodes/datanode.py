from contextlib import redirect_stdout
from datanodes.core.node_properties import NodeProperties
from datanodes.graphics.graphics_view import MODE_DRAG_RESIZE, MODE_NONE
from datanodes.core.utils import dumpException
from datanodes.core.node_node import Node
from datanodes.core.node_content_widget import NodeContentWidget
from datanodes.graphics.graphics_node import GraphicsNode
from PyQt5.QtWidgets import QGridLayout, QToolButton, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QRectF, QRect, QSize, Qt
from PyQt5.QtGui import QIcon, QImage
from datanodes.core.node_socket import *
import os
import pandas as pd
import numpy as np

class Pair():
    old = ""
    new = ""
    len = 0
    def __init__(self, old="", new="", len=0):
        self.old = old
        self.new = new
        self.len = len

DEBUG = False

class DataGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180
        self.height = 100
    
    def initAssets(self):
        super().initAssets()
        path = os.path.dirname(os.path.abspath(__file__))
        self.icons    = QImage(os.path.join(path, "../icons/status_icons.png"))
        self.drag_img = QImage(os.path.join(path, "../icons/drag.png"))
    
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        offset = 24.0
        brush =  self._brush_title
        
        if self.node.isDirty()   : 
            offset =  0.0
            brush = self._brush_dirty
            
        if self.node.isInvalid() : 
            offset = 48.0
            brush  = self._brush_invalid

        if self.node.isMute() : 
            offset = 24.0
            brush  = self._brush_mute
        
        if self.node.isBusy() : 
            offset = 72.0
            brush  = self._brush_busy

        self.paintTitle(painter, brush)

        painter.drawImage(
            QRectF(-10.0, -10.0, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0.0, 24.0, 24.0)
            )
        

    def itemChange(self, change, value):
        if self.isSelected() and not self.is_selected:
            self.is_selected = True
        else:
            self.is_selected = False
        return super().itemChange(change, value)

class DataContent(NodeContentWidget):
    changed      = pyqtSignal()
    removed      = pyqtSignal(Socket)
    outchanged   = pyqtSignal()
    renamed      = pyqtSignal(Pair)
    mainWidget   = None

    def initUI(self):
        pass
            
    def updateSize(self):
        x, y = (self.node.grNode.width - 2.0 * self.node.grNode.padding, 
                self.node.grNode.height - (self.node.grNode.title_height + 2.0 * self.node.grNode.padding + 1))
        self.resize(int(x), int(y))
        
    def onCopy(self):
        return False
    
    def onPaste(self):
        return False
    
    def onSelected(self):
        pass

    def onDeselected(self):
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
        # Mark all nodes dirty by default before it is connected to anything
        self.setDirty()
        self.eval()

    def initInnerClasses(self):
        self.content    = DataContent(self)
        self.grNode     = DataGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.eval)
        self.content.removed.connect(self.eval)

    def onSelected(self):
        self.scene.window.propertiesDock.setPropertyWidget(self.properties)

    def onDeselected(self):
        self.properties.setParent(None)
        self.scene.window.propertiesDock.setPropertyWidget(None)


    def initSettings(self):
        super().initSettings()
        self.socket_spacing = 24.0
        self.socket_padding = 20.0
        self.socket_top_margin = 40.0
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER


    def isString(self, x):
        try:
            float(x)
            return False
        except:
            return True

    def getFormatedValue(self, value):
        # check if value is string
        if isinstance(value, str) : return value
        
        # format the int value
        if isinstance(value, int) : return value
        
        # format the double value
        if not self.isString(value):
            if str(value) == ""           : return ""
            if np.isnan(value)            : return "nan"
            if np.isinf(value)            : return "inf"

            if np.abs(value) > 1000000.0                            : return "{:.3e}".format(value)
            if np.abs(value) > 1000.0 and np.abs(value) <= 1000000.0: return "{:.3e}".format(value)
            if np.abs(value) > 100.0 and np.abs(value) <= 1000.0    : return "{:.2f}".format(value)
            if np.abs(value) > 1.0 and np.abs(value) <= 100.0       : return "{:.3f}".format(value)
            if np.abs(value) > 0.01 and np.abs(value) <= 1.0        : return "{:.4f}".format(value)
            if np.abs(value) > 0.00 and np.abs(value) <= 0.01       : return "{:.3e}".format(value)
            else                                                    : return "{:.1f}".format(value)
        else:
            return value


    def evalImplementation(self, silent=False):
        return 123

    # ---------------- Input sockets functionality ------------
    def sortSockets(self):
        pass

    def appendNewSocket(self):
        pass

    def getSocketsNames(self):
        pass

    def updateInputSockets(self):
        self.removeFreeInputs()
        self.sortSockets()
        self.appendNewSocket()
        self.getSocketsNames()

    def updateOutputSockes(self):
        pass

    def recalculateNode(self):
        self.updateInputSockets()
        self.updateOutputSockes()
        self.setDirty()
        self.eval()

    def rename(self, dict):
        print(self._title)
        print("dict : ", dict.old, dict.new)
        print("before", self.value)

        if dict.new != dict.old and dict.new in self.value:
            self.setDirty()
            self.setDescendentsDirty()
            self.eval(False)
            self.evalChildren(False)
            return

        if dict.len != self.getValueSize():
            self.setDirty()
            self.setDescendentsDirty()
            self.eval(False)
            self.evalChildren(False)
            return

        if dict.old in self.value:
            self.value = {dict.new if k == dict.old else k : v for k, v in self.value.items()}

        print("after", self.value)

        self.updateNames(dict)
        self.updateOutputs()
        
        for other_node in self.getChildNodes():
            other_node.rename(dict)

    def getValueSize(self):
        return len(self.value)       

    def updateNames(self, dict):
        pass

    def updateOutputs(self):
        if self.hasOutput() : self.getOutput(0).value = self.value
        

    def eval(self, silent=False):
        if not self.isDirty() and not self.isInvalid() and not self.recalculate:
            #return self.value
            return True
        try:
            if self.isMute():
                if len(self.getInputs()) > 0:
                    val_label = list(self.getInput(0).value.keys())[0]
                    value = self.getInput(0).value
                else:
                    value = {"x" : 0.0}
                
                if len(self.getOutputs()) > 0:
                    self.getOutput(0).value = value
                self.setDescendentsDirty()
                self.evalChildren()
                return True

            elif self.evaluateNode(silent):
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
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


    def evaluateNode(self, silent=False):
        if not self.getInputData() :       return False
        if not self.prepareSettings() :    return False
        if not self.evalImplementation(silent) : return False
        return True


    def getInputData(self):
        input_edge = self.getInput(0)
        if not input_edge:
            return True
        else:            
            try:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = input_edge.value
                self.type  = input_edge.type
            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = e
                return False
        return True

    def prepareSettings(self):
        return True



    def reEvaluate(self):
        self.setDirty()
        self.eval()

    def onInputChanged(self, new_edge=None):
        if DEBUG : print("DATANODE : oninputChanged")
        self.setDirty()
        if DEBUG : print("DATANODE : to run the eval")
        self.eval()
        if DEBUG : print("DATANODE : the eval is done")
        self.content.changed.emit()

    def onInputRemoved(self, socket=None):
        if DEBUG : print("DATANODE : oninputRemoved")
        self.setDirty()
        if DEBUG : print("DATANODE : to run the eval")
        self.eval()
        if DEBUG : print("DATANODE : the eval is done")
        self.content.removed.emit(socket)

    def onOutputChanged(self, new_edge=None):
        pass

    def onOutputRemoved(self, new_edge=None):
        pass

    def getInputVaue(self, value, default=0):
        num = default
        if isinstance(value, dict):
            num = self.dictFirstValue(value)
        if isinstance(value, float):
            num = value
        if isinstance(value, int):
            num = value
        if isinstance(value, (list, np.ndarray)):
            num = value
        return num

    def getInputLength(self, value, default=0):
        num = default
        if isinstance(value, dict):
            if self.lenOrValOfDict(value) == 1:
                num = int(self.dictFirstValue(value))
            else:
                num = self.lenOrValOfDict(value)

        if isinstance(value, float):
            num = int(value)
        if isinstance(value, int):
            num = value
        if isinstance(value, (list, np.ndarray)):
            if len(value) == 1:
                num = value[0]
            else:
                num = len(value)
        return num

    def dictFirstValue(self, obj, default=0):
        if len(obj) == 0:
            return 0
        res = 0
        if len(obj) == 1:
            for name in obj:
                if isinstance(obj[name], (list, np.ndarray)):
                    res = obj[name][0]
                if isinstance(obj[name], float) or isinstance(obj[name], int):
                    res = obj[name]
            return res
        return default


    def lenOrValOfDict(self, obj):
        if len(obj) == 0:
            return 0
        res = 0
        if len(obj) == 1:
            for name in obj:
                if isinstance(obj[name], (list, np.ndarray)):
                    res = len(obj[name])
                if isinstance(obj[name], float) or isinstance(obj[name], int):
                    res = 1
            return res

        res = 0
        for name in obj:
            res += len(obj[name])
        return res

    def updateOutputsPos(self):
        if self.getOutputs():
            for i, soket in enumerate(self.getOutputs()):
                soket.index = i
                soket.setPos()

    def updateInputsPos(self):
        if self.getInputs():
            for i, soket in enumerate(self.getInputs()):
                soket.index = i
                soket.setPos()


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
            width  = self.init_size[0] + scale.x()
            height = self.init_size[1] + scale.y()
            if width  > self.min_width  : self.width  = width
            if height > self.min_height : self.height = height
            self.update()
            self.node.updateOutputsPos()
            self.content.updateSize()
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





class ResizableGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 80
        self.min_height = 80

class ResizableContent(DataContent):
    def initUI(self):
        super().initUI()
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)
        self.labels = {}
        self.values = {}

    def serialize(self):
        res = super().serialize()
        res['width']  = self.node.grNode.width
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.updateSize()
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res








class ResizableInputNode(DataNode):
    icon = "icons/math.png"
    op_code = 0
    op_title = ""

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin = 20.0

    def initInnerClasses(self):
        self.content    = ResizableContent(self)
        self.grNode     = ResizableGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def resize(self):
        size = len(self.getInputs())
        current_size = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin

        if current_size > self.grNode.min_height:
            self.grNode.height = current_size
            self.grNode.update()
            self.content.updateSize()


    def appendNewSocket(self):
        if self.freeInputs() == 0:
            self.appendInput(input=1)
            self.resize()
        self.scene.grScene.update()

    def sortSockets(self):
        sockets_full = []
        sockets_empty = []
        for socket in self.getInputs():
            if socket.hasEdges():
                sockets_full.append(socket)
            else:
                sockets_empty.append(socket)

        for i, socket in zip(range(len(sockets_full + sockets_empty)), sockets_full + sockets_empty):
            socket.index = i
            socket.setPos()

        self.inputs = sockets_full + sockets_empty
        self.scene.grScene.update()

    def removeFreeInputs(self):
        for input in self.inputs[:-1]:
            if not input.hasEdges(): 
                input.grSocket.hide()
                self.scene.grScene.removeItem(input.grSocket)
        self.inputs = [input for input in self.inputs if input.hasEdges() or input == self.inputs[-1]]
        self.resize()
        self.scene.grScene.update()

    def getSocketsNames(self):
        if len(self.inputs) == 0: 
            return None

        for socket in self.inputs:
            if socket.hasEdges():
                edge = socket.edges[0]
                other_socket = edge.getOtherSocket(socket)
                if isinstance(other_socket.value, pd.Series):                
                    socket.label = other_socket.value.name
                if isinstance(other_socket.value, dict):
                    if other_socket.value is not None and len(other_socket.value) > 0:
                        if len(other_socket.value) == 1:
                            socket.label = list(other_socket.value.keys())[0]
                        else:
                            socket.label = str(list(other_socket.value.keys())[0]) + "..."
                    
    def evalImplementation(self, silent=False):
        pass

    def update(self, silent=False):
        super().update(silent)
        self.recalculateNode()

    def getDataLimits(self):
        xmin  = 1.0e20
        xmax  =-1.0e20
        ymin  = 1.0e20
        ymax  =-1.0e20
        sxmin = 0.0
        sxmax = 0.0
        symin = 0.0
        symax = 0.0
        
        for input in self.insockets:
            if not input.value : return 0.0 * (1.0 - sxmin) + sxmin * xmin, 1.0 * (1.0 - sxmax) + sxmax * xmax, 0.0 * (1.0 - symin) + symin * ymin, 1.0 * (1.0 - symax) + symax * ymax

            x_name = list(input.value.keys())[0]
            x_val  = input.value[x_name]

            if np.any(x_val):
                if min(x_val) < xmin : 
                    xmin  = min(x_val)
                    sxmin = 1.0
                if max(x_val) > xmax : 
                    xmax  = max(x_val)
                    sxmax = 1.0

            for name in list(input.value)[1:]:
                y_val  = input.value[name]
                
                if not np.any(y_val): continue
            
                if min(y_val) < ymin : 
                    ymin  = min(y_val)
                    symin = 1.0
                
                if max(y_val) > ymax : 
                    ymax  = max(y_val)
                    symax = 1.0
        
        return 0.0 * (1.0 - sxmin) + sxmin * xmin, 1.0 * (1.0 - sxmax) + sxmax * xmax, 0.0 * (1.0 - symin) + symin * ymin, 1.0 * (1.0 - symax) + symax * ymax










class ResizableOutputNode(DataNode):
    icon = "icons/math.png"
    op_code = 0
    op_title = ""

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin = 20

    def initInnerClasses(self):
        self.content = ResizableContent(self)
        self.grNode  = ResizableGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def appendNewSocket(self):
        self.appendOutput(output=2)
        self.content.appendPair(self.outputs[-1])

        size = len(self.getOutputs())
        current_size = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin
        
        if current_size > self.grNode.min_height:
            self.grNode.height = current_size
            self.grNode.update()
            self.content.updateSize()

    def sortSockets(self):
        sockets_full = []
        sockets_empty = []
        if self.getOutputs():
            for socket in self.getOutputs():
                if socket.hasEdges():
                    sockets_full.append(socket)
                else:
                    sockets_empty.append(socket)

            for i, socket in zip(range(len(sockets_full + sockets_empty)), sockets_full + sockets_empty):
                socket.index = i
                socket.setPos()

            self.outputs = sockets_full + sockets_empty


    def getSocketsNames(self):
        if len(self.inputs) == 0: 
            return None

        for socket in self.inputs:
            if socket.hasEdges():
                edge = socket.edges[0]
                other_socket = edge.getOtherSocket(socket)
                if isinstance(other_socket.value, pd.Series):                
                    socket.label = other_socket.value.name
                if isinstance(other_socket.value, dict):
                    if other_socket.value is not None and len(other_socket.value) > 0:
                        if len(other_socket.value) == 1:
                            socket.label = list(other_socket.value.keys())[0]
                        else:
                            socket.label = str(list(other_socket.value.keys())[0]) + "..."
                    
    def evalImplementation(self, silent=False):
        pass

    def update(self, silent=False):
        super().update(silent)






class ResizableInOutNode(DataNode):
    icon = "icons/math.png"
    op_code = 0
    op_title = ""

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin = 20

    def initInnerClasses(self):
        self.content = ResizableContent(self)
        self.grNode  = ResizableGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def resize(self):
        size = len(self.getInputs())
        current_size = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin

        padding_title = self.grNode.title_height + 2.0 * self.grNode.padding

        if current_size > self.grNode.min_height:
            self.grNode.height = current_size
            self.grNode.update()
            self.content.updateSize()


    def appendNewSocket(self):
        if self.freeInputs() == 0:
            self.appendInput(input=1)
            self.resize()

    def sortSockets(self):
        sockets_full = []
        sockets_empty = []
        for socket in self.inputs:
            if socket.hasEdges():
                sockets_full.append(socket)
            else:
                sockets_empty.append(socket)

        for i, socket in zip(range(len(sockets_full + sockets_empty)), sockets_full + sockets_empty):
            socket.index = i
            socket.setPos()

        self.inputs = sockets_full + sockets_empty
        self.removeFreeInputs()
        self.appendNewSocket()

    def removeFreeInputs(self):
        for input in self.inputs[:-1]:
            if not input.hasEdges(): 
                input.grSocket.hide()
                self.scene.grScene.removeItem(input.grSocket)
        self.inputs = [input for input in self.inputs if input.hasEdges() or input == self.inputs[-1]]
        self.resize()
        self.scene.grScene.update()

    def getSocketsNames(self):
        if len(self.inputs) == 0: 
            return None

        for socket in self.inputs:
            if socket.hasEdges():
                edge = socket.edges[0]
                other_socket = edge.getOtherSocket(socket)
                if isinstance(other_socket.value, pd.Series):                
                    socket.label = other_socket.value.name
                if isinstance(other_socket.value, dict):
                    if other_socket.value is not None and len(other_socket.value) > 0:
                        if len(other_socket.value) == 1:
                            socket.label = list(other_socket.value.keys())[0]
                        else:
                            socket.label = str(list(other_socket.value.keys())[0]) + "..."
                    
    def evalImplementation(self, silent=False):
        pass

    def update(self, silent=False):
        super().update(silent)











class RemoveButton(QToolButton):
    def __init__(self, content, id=None):
        super().__init__()
        self.initUI()
        self.content = content
        self.id      = id

    def initUI(self):
        self.setWindowTitle("RemoveButton")
        self.setGeometry(QRect(0, 0, 24, 24))
        path = os.path.dirname(os.path.abspath(__file__))
        self.icon    = QIcon(os.path.join(path, "../icons/remove.png"))
        self.setIcon(self.icon)   #icon
        self.setIconSize(QSize(16,16))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setToolTip("Remove the variable") #Tool tip

    def removePair(self):
        self.content.mainlayout.removeWidget(self.content.labels[self.id])
        self.content.mainlayout.removeWidget(self.content.values[self.id])
        self.content.mainlayout.removeWidget(self.content.remove[self.id])
        self.content.labels[self.id].setParent(None)
        self.content.values[self.id].setParent(None)
        self.content.remove[self.id].setParent(None)
        del self.content.labels[self.id]
        del self.content.values[self.id]
        self.content.node.resize()
        self.content.sortWidgets()
#        del self.content.remove[self.id]

class AdjustableOutputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200
        self.height = 220
        self.min_height = 220
        self.min_width  = 120

class AdjustableOutputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.vlayout    = QVBoxLayout()
        self.mainlayout = QGridLayout()
        self.vlayout.setContentsMargins(0, 2, 0, 2)
        self.mainlayout.setContentsMargins(0,0,0,0)

        self.addItems = QPushButton()
        self.addItems.setText("append variable")

        self.vlayout.addLayout(self.mainlayout)
        self.vlayout.addWidget(self.addItems)
        self.setLayout(self.vlayout)

    def serialize(self):
        res = super().serialize()
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.updateSize()
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res

class AdjustableOutputNode(DataNode):
    icon = "icons/math.png"
    op_code = 0
    op_title = ""

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin = 20.0

    def initInnerClasses(self):
        self.content = AdjustableOutputContent(self)
        self.grNode  = AdjustableOutputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def evalImplementation(self, silent=False):
        pass


