
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *


class ValueInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140.0
        self.height = 70.0

class ValueInputContent(DataContent):
    def initUI(self):
        super().initUI()
  
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)

        self.label = QLineEdit("x", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.value = QLineEdit("1.0", self)
        self.value.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.label, 0, 0)
        self.mainlayout.addWidget(self.value, 0, 1)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.value.text()
        res['label'] = self.label.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.value.setText(data['value'])
            self.label.setText(data['label'])
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_VALINPUT)
class ValueInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_VALINPUT
    op_title = "Value"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = ValueInputContent(self)
        self.grNode  = ValueInputGraphicsNode(self)
        self.content.value.returnPressed.connect(self.onInputChanged)
        self.content.label.returnPressed.connect(self.onInputChanged)
        self.content.changed.connect(self.recalculateNode)    
        
    def evalImplementation(self):
        try:
            u_value = self.content.value.text()
            s_value = float(u_value)
            label   = self.content.label.text()
            self.getOutput(0).value = {label : s_value}
            self.getOutput(0).type  = "float"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            self.setInvalid()
            return False






class MultiValueInputGraphicsNode(ResizableOutputGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140.0
        self.height = 70.0
        self.min_height = 70.0

class MultiValueInputContent(ResizableOutputContent):
    def initUI(self):
        super().initUI()
        self.mainlayout.setSpacing(0)
        self.labels = {}
        self.values = {}

    def appendPair(self, socket, at=None):
        if self.labels and not at:
            i = len(self.labels)
        elif at:
            i = at
        else:
            i = 0
        self.labels[str(socket.id)]  = QLineEdit("x"+str(i), self)
        self.labels[str(socket.id)].setAlignment(Qt.AlignRight)
        self.values[str(socket.id)]  = QLineEdit("1.0", self)
        self.values[str(socket.id)].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.labels[str(socket.id)], i, 0)
        self.mainlayout.addWidget(self.values[str(socket.id)], i, 1)
        self.labels[str(socket.id)].textChanged.connect(self.node.recalculateNode)
        self.values[str(socket.id)].textChanged.connect(self.node.recalculateNode)

    def clearContent(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels.clear()
        self.values.clear()

    def clearFromLayout(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            if child.widget():
                self.mainlayout.removeItem(child)
                child.widget().deleteLater()

    def movePairTo(self, socket, at):
        self.mainlayout.removeWidget(self.labels[str(socket.id)])
        self.mainlayout.removeWidget(self.values[str(socket.id)])
        self.mainlayout.addWidget(self.labels[str(socket.id)], at, 0)
        self.mainlayout.addWidget(self.values[str(socket.id)], at, 1)


    def removePair(self, socket):
        self.mainlayout.removeWidget(self.labels[str(socket.id)])
        self.mainlayout.removeWidget(self.values[str(socket.id)])
        self.labels[str(socket.id)].setParent(None)
        self.values[str(socket.id)].setParent(None)
        del self.labels[str(socket.id)]
        del self.values[str(socket.id)]

    def serialize(self):
        res = super().serialize()
        """
        res['value'] = self.values[0].text()
        res['label'] = self.labels[0].text()
        """
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            """
            self.values[0].setText(data['value'])
            self.labels[0].setText(data['label'])
            """
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_MULVALINPUT)
class MultiValueInputNode(ResizableOutputNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_MULVALINPUT
    op_title = "Multi-Value"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.content.appendPair(self.getOutput(0))
        self.eval()
        self.timer = None

    def onEdgeConnectionChanged(self, new_edge=None):
        self.recalculateNode()

    def initInnerClasses(self):
        self.content = MultiValueInputContent(self)
        self.grNode  = MultiValueInputGraphicsNode(self)
        self.content.changed.connect(self.recalculateNode)

    def resize(self):
        size = len(self.getOutputs())
        current_size  = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin

        padding_title = self.grNode.title_height + 2.0 * self.grNode.padding
        if current_size > self.grNode.min_height:
            self.grNode.height = current_size
            self.grNode.update()

            x, y = self.grNode.width - 2.0 * self.grNode.padding, current_size - padding_title + 1
            self.content.resize(x, y)
        self.scene.grScene.update()

    def appendNewSocket(self):
        if self.freeOutputs() == 0:
            self.appendOutput(output=2)


    def sortSockets(self):
        sockets_full  = []
        sockets_empty = []
        labels_full = {}
        values_full = {}
        labels_empty = {}
        values_empty = {}
        for socket in self.getOutputs():
            if socket.hasEdges():
                sockets_full.append(socket)
                labels_full[str(socket.id)] = self.content.labels[str(socket.id)]
                values_full[str(socket.id)] = self.content.values[str(socket.id)]
            else:
                sockets_empty.append(socket)
                labels_empty[str(socket.id)] = self.content.labels[str(socket.id)]
                values_empty[str(socket.id)] = self.content.values[str(socket.id)]

        self.outputs = sockets_full + sockets_empty

        self.removeFreeSocketsWithPairs()
        #self.removeFreeOutputs()
        self.appendNewSocket()

        for i, socket in zip(range(len(self.outputs)), self.outputs):
            socket.index = i
            socket.setPos()

        for i, socket in zip(range(len(self.getOutputs())), self.getOutputs()):
            if str(socket.id) not in self.content.labels:
                self.content.appendPair(socket, at=i)
            if str(socket.id) in self.content.labels:
                self.content.movePairTo(socket, at=i)

        # The timer is set here
        self.timer = QTimer()
        self.timer.timeout.connect(self.resize)
        self.timer.start(1)


    def removeFreeSocketsWithPairs(self):
        for output in self.outputs[:-1]:
            if not output.hasEdges(): 
                output.grSocket.hide()
                self.scene.grScene.removeItem(output.grSocket)
                self.content.removePair(output)
        self.outputs = [output for output in self.outputs if output.hasEdges() or output == self.outputs[-1]]


    def evalImplementation(self):
        try:
            self.sortSockets()
            for socket in self.getOutputs():
                u_value = self.content.values[str(socket.id)].text()
                s_value = float(u_value)
                label   = self.content.labels[str(socket.id)].text()
                socket.value = {label : s_value}
                socket.type  = "float"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            self.setInvalid()
            return False
