
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.core.node_settings import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import QTimer

class ValueInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140
        self.height = 70

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
        self.properties = NodeProperties(self)
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
        self.width  = 200
        self.height = 100
        self.min_height = 100

class MultiValueInputContent(AdjustableOutputContent):
    def initUI(self):
        super().initUI()
        self.mainlayout.setSpacing(0)
        self.remove = {}
        self.labels = {}
        self.values = {}

    def appendPair(self, at=None):
        if self.labels and not at:
            i = len(self.labels)
        elif at:
            i = at
        else:
            i = 0
        
        id = str(int(np.random.rand()*1000000))
        while id in self.labels : id = str(int(np.random.rand()*1000000))

        self.remove[id]  = RemoveButton(self, id)
        self.labels[id]  = QLineEdit("x"+str(i), self)
        self.labels[id].setAlignment(Qt.AlignRight)
        self.values[id]  = QLineEdit("1.0", self)
        self.values[id].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.remove[id], i, 0)
        self.mainlayout.addWidget(self.labels[id], i, 1)
        self.mainlayout.addWidget(self.values[id], i, 2)

        self.labels[id].returnPressed.connect(self.node.recalculateNode)
        self.values[id].returnPressed.connect(self.node.recalculateNode)
        self.remove[id].clicked.connect(self.remove[id].removePair)


    def sortWidgets(self):
        for i, key in enumerate(self.labels):
            self.remove[key].setParent(None)
            self.labels[key].setParent(None)
            self.values[key].setParent(None)

        for i, key in enumerate(self.labels):
            self.mainlayout.addWidget(self.remove[key], i, 0)
            self.mainlayout.addWidget(self.labels[key], i, 1)
            self.mainlayout.addWidget(self.values[key], i, 2)

    def serialize(self):
        res     = super().serialize()
        labels  = []
        values  = []
        ids     = []
        for key in self.labels:
            labels.append(self.labels[key].text())
            values.append(self.values[key].text())
            ids.append(key)

        res['value'] = values
        res['label'] = labels
        res['id']    = ids
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            for i, id, label, value in zip(range(len(data['label'])), data['id'], data['label'], data['value']):
                self.remove[id]  = RemoveButton(self, id)
                self.labels[id]  = QLineEdit(label, self)
                self.labels[id].setAlignment(Qt.AlignRight)
                self.values[id]  = QLineEdit(value, self)
                self.values[id].setAlignment(Qt.AlignLeft)

                self.mainlayout.addWidget(self.remove[id], i, 0)
                self.mainlayout.addWidget(self.labels[id], i, 1)
                self.mainlayout.addWidget(self.values[id], i, 2)
                self.remove[id].clicked.connect(self.remove[id].removePair)
                self.labels[id].returnPressed.connect(self.node.recalculateNode)
                self.values[id].returnPressed.connect(self.node.recalculateNode)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_MULVALINPUT)
class MultiValueInputNode(AdjustableOutputNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_MULVALINPUT
    op_title = "Multi-Value"

    def __init__(self, scene, inputs=[], outputs=[SOCKET_TYPE_DATA]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()
        self.timer = None

    def onEdgeConnectionChanged(self, new_edge=None):
        self.recalculateNode()

    def initInnerClasses(self):
        self.content = MultiValueInputContent(self)
        self.grNode  = MultiValueInputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)
        self.content.addItems.clicked.connect(self.appendNewPair)

    def resize(self):
        try:
            size = len(self.content.labels)
            current_size  = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin + 30.0
            padding_title = self.grNode.title_height + 2.0 * self.grNode.padding
            if current_size > self.grNode.min_height:
                self.grNode.height = current_size
                self.grNode.update()
                self.content.updateSize()
            self.scene.grScene.update()
        except Exception as e : pass
        

    def appendNewPair(self):
        self.content.appendPair()
        # The timer is set here
        self.timer = QTimer()
        self.timer.timeout.connect(self.resize)
        self.timer.start(1)


    def evalImplementation(self, silent=False):
        try:
            if self.getOutputs():
                self.value = {}
                for id in self.content.values:
                    value = float(self.content.values[id].text())
                    label = self.content.labels[id].text()
                    self.value[label] = value

                self.getOutput(0).value = self.value
                self.getOutput(0).type  = "df"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            self.setInvalid()
            return False
