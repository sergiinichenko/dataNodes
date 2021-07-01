
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class MathGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 100.0

class MathContent(DataContent):

    def initUI(self):
        super().initUI()
        self.operation = "Add"
        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.cb.addItem("Add")
        self.cb.addItem("Substract")
        self.cb.addItem("Multiply")
        self.cb.addItem("Divide")
        self.cb.addItem("Power")

        layout.addWidget(self.cb)
        self.setLayout(layout)
        self.setWindowTitle("Math node")
        self.cb.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        self.operation = self.cb.currentText()
        self.changed.emit()

    def serialize(self):
        res = super().serialize()
        res['sel_ind'] = self.cb.currentIndex()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['sel_ind']
            self.cb.setCurrentIndex(value)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_MATH)
class MathNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_MATH
    op_title = "Math"

    def __init__(self, scene, inputs=[1,1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = MathContent(self)
        self.grNode  = MathGraphicsNode(self)
        self.content.changed.connect(self.reEvaluate)

    def evalImplementation(self):
        input_nodes = self.getInputs()
        if not input_nodes:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:      
            if len(input_nodes) == 2:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                if self.content.operation == "Add"      : self.value = self.add(input_nodes)
                if self.content.operation == "Substract": self.value = self.substract(input_nodes)
                if self.content.operation == "Multiply" : self.value = self.multiply(input_nodes)
                if self.content.operation == "Divide"   : self.value = self.devide(input_nodes)
                if self.content.operation == "Power"    : self.value = self.power(input_nodes)
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not all input nodes are connected"
                self.value = 0
                return False

    def add(self, input_nodes):
        val = 0
        for node in input_nodes: val += node.value
        return val

    def substract(self, input_nodes):
        val = input_nodes[0].value
        for node in input_nodes[1:]: val -= node.value
        return val

    def multiply(self, input_nodes):
        val = input_nodes[0].value
        for node in input_nodes[1:]: val *= node.value
        return val

    def devide(self, input_nodes):
        val = input_nodes[0].value
        for node in input_nodes[1:]: val /= node.value
        return val

    def power(self, input_nodes):
        val = input_nodes[0].value
        for node in input_nodes[1:]: val = pow(val, node.value)
        return val
