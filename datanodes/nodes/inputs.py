
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




class MultiValueInputGraphicsNode(AdjustableOutputGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 100.0
        self.min_height = 100.0

class MultiValueInputContent(AdjustableOutputContent):
    def initUI(self):
        super().initUI()
        self.mainlayout.setSpacing(0)
        self.remove = {}
        self.labels = {}
        self.values = {}

    def appendPair(self, socket, at=None):
        if self.labels and not at:
            i = len(self.labels)
        elif at:
            i = at
        else:
            i = 0
        self.remove[str(socket.id)]  = RemoveButton(str(socket.id))
        self.labels[str(socket.id)]  = QLineEdit("x"+str(i), self)
        self.labels[str(socket.id)].setAlignment(Qt.AlignRight)
        self.values[str(socket.id)]  = QLineEdit("1.0", self)
        self.values[str(socket.id)].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.remove[str(socket.id)], i, 0)
        self.mainlayout.addWidget(self.labels[str(socket.id)], i, 1)
        self.mainlayout.addWidget(self.values[str(socket.id)], i, 2)

        self.labels[str(socket.id)].textChanged.connect(self.node.recalculateNode)
        self.values[str(socket.id)].textChanged.connect(self.node.recalculateNode)
        self.remove[str(socket.id)].clicked.connect(lambda : self.removePair(socket))

    def clearContent(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels.clear()
        self.values.clear()
        self.remove.clear()

    def removePair(self, soket):
        self.mainlayout.removeWidget(self.labels[str(soket.id)])
        self.mainlayout.removeWidget(self.values[str(soket.id)])
        self.mainlayout.removeWidget(self.remove[str(soket.id)])
        self.labels[str(soket.id)].setParent(None)
        self.values[str(soket.id)].setParent(None)
        self.remove[str(soket.id)].setParent(None)
        del self.labels[str(soket.id)]
        del self.values[str(soket.id)]
        #del self.remove[str(soket.id)]

        self.node.resize()
        self.node.removeOutput(soket)
        self.sortWidgets()
    
    def clearContent(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            #if child.widget():
            #    child.widget().deleteLater()    

    def sortWidgets(self):
        for i, soket in zip(range(len(self.labels)), self.node.getOutputs()):
            self.remove[str(soket.id)].setParent(None)
            self.labels[str(soket.id)].setParent(None)
            self.values[str(soket.id)].setParent(None)

        for i, soket in zip(range(len(self.labels)), self.node.getOutputs()):
            self.mainlayout.addWidget(self.remove[str(soket.id)], i, 0)
            self.mainlayout.addWidget(self.labels[str(soket.id)], i, 1)
            self.mainlayout.addWidget(self.values[str(soket.id)], i, 2)
            soket.index = i
            soket.setPos()


    def serialize(self):
        res = super().serialize()
        labels = []
        values = []
        sockets = []

        for label, value in zip(self.labels, self.values):
            labels.append(self.labels[label].text())
            values.append(self.values[value].text())
            sockets.append(label)
        res['value'] = values
        res['label'] = labels
        res['socket'] = sockets
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.clearContent()
            for i, socket, label, value in zip(range(len(data['socket'])), data['socket'], data['label'], data['value']):
                self.remove[socket]  = RemoveButton(socket)
                self.labels[socket]  = QLineEdit("x"+str(i), self)
                self.labels[socket].setAlignment(Qt.AlignRight)
                self.labels[socket].setText(label)
                self.values[socket]  = QLineEdit("1.0", self)
                self.values[socket].setAlignment(Qt.AlignLeft)
                self.values[socket].setText(value)
                self.mainlayout.addWidget(self.remove[socket], i, 0)
                self.mainlayout.addWidget(self.labels[socket], i, 1)
                self.mainlayout.addWidget(self.values[socket], i, 2)
                self.remove[socket].clicked.connect(lambda:self.removePair(socket))
                self.labels[socket].textChanged.connect(self.node.recalculateNode)
                self.values[socket].textChanged.connect(self.node.recalculateNode)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_MULVALINPUT)
class MultiValueInputNode(AdjustableOutputNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_MULVALINPUT
    op_title = "Multi-Value"

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.appendNewPair()
        self.eval()
        self.timer = None

    def onEdgeConnectionChanged(self, new_edge=None):
        self.recalculateNode()

    def initInnerClasses(self):
        self.content = MultiValueInputContent(self)
        self.grNode  = MultiValueInputGraphicsNode(self)
        self.content.changed.connect(self.recalculateNode)
        self.content.addItems.clicked.connect(self.appendNewPair)

    def resize(self):
        try:
            size = len(self.getOutputs())
            current_size  = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin + 30.0
            padding_title = self.grNode.title_height + 2.0 * self.grNode.padding
            if current_size > self.grNode.min_height:
                self.grNode.height = current_size
                self.grNode.update()

                x, y = self.grNode.width - 2.0 * self.grNode.padding, current_size - padding_title + 1
                self.content.resize(x, y)
            self.scene.grScene.update()
        except Exception as e : pass
        

    def appendNewPair(self):
        self.appendOutput(output=2)
        self.content.appendPair(self.getOutputs()[-1])
        # The timer is set here
        self.timer = QTimer()
        self.timer.timeout.connect(self.resize)
        self.timer.start(1)


    def evalImplementation(self):
        try:
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
