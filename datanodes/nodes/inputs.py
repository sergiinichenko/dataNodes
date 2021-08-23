
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
        self.properties = DataProperties(self)
        self.content.value.returnPressed.connect(self.onInputChanged)
        self.content.label.returnPressed.connect(self.onInputChanged)
        self.content.changed.connect(self.recalculateNode)    
        
    def evalImplementation(self, silent=False):
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
        self.width  = 200.0
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
        self.remove[str(socket.id)]  = RemoveButton(self, str(socket.id))
        self.labels[str(socket.id)]  = QLineEdit("x"+str(i), self)
        self.labels[str(socket.id)].setAlignment(Qt.AlignRight)
        self.values[str(socket.id)]  = QLineEdit("1.0", self)
        self.values[str(socket.id)].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.remove[str(socket.id)], i, 0)
        self.mainlayout.addWidget(self.labels[str(socket.id)], i, 1)
        self.mainlayout.addWidget(self.values[str(socket.id)], i, 2)

        self.labels[str(socket.id)].textChanged.connect(self.node.recalculateNode)
        self.values[str(socket.id)].textChanged.connect(self.node.recalculateNode)
        self.remove[str(socket.id)].clicked.connect(self.remove[str(socket.id)].removePair)

    
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
        res     = super().serialize()
        labels  = []
        values  = []
        sockets = []

        for key in self.labels:
            labels.append(self.labels[key].text())
            values.append(self.values[key].text())
            sockets.append(key)
        res['value'] = values
        res['label'] = labels
        res['socket'] = sockets
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            for i, socket, label, value in zip(range(len(data['label'])), self.node.getOutputs(), data['label'], data['value']):
                self.remove[str(socket.id)]  = RemoveButton(self, str(socket.id))
                self.labels[str(socket.id)]  = QLineEdit(label, self)
                self.labels[str(socket.id)].setAlignment(Qt.AlignRight)
                self.values[str(socket.id)]  = QLineEdit(value, self)
                self.values[str(socket.id)].setAlignment(Qt.AlignLeft)

                self.mainlayout.addWidget(self.remove[str(socket.id)], i, 0)
                self.mainlayout.addWidget(self.labels[str(socket.id)], i, 1)
                self.mainlayout.addWidget(self.values[str(socket.id)], i, 2)
                self.remove[str(socket.id)].clicked.connect(self.remove[str(socket.id)].removePair)
                self.labels[str(socket.id)].textChanged.connect(self.node.recalculateNode)
                self.values[str(socket.id)].textChanged.connect(self.node.recalculateNode)
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
        self.eval()
        self.timer = None

    def onEdgeConnectionChanged(self, new_edge=None):
        self.recalculateNode()

    def initInnerClasses(self):
        self.content = MultiValueInputContent(self)
        self.grNode  = MultiValueInputGraphicsNode(self)
        self.properties = DataProperties(self)
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


    def evalImplementation(self, silent=False):
        try:
            if self.getOutputs():
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
