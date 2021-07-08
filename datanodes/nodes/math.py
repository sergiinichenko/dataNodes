
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
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:      
            if len(input_edges) == 2:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                if self.content.operation == "Add"      : self.outputs[0].value = self.add(input_edges)
                if self.content.operation == "Substract": self.outputs[0].value = self.substract(input_edges)
                if self.content.operation == "Multiply" : self.outputs[0].value = self.multiply(input_edges)
                if self.content.operation == "Divide"   : self.outputs[0].value = self.devide(input_edges)
                if self.content.operation == "Power"    : self.outputs[0].value = self.power(input_edges)
                self.outputs[0].type = "float"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not all input nodes are connected"
                self.outputs[0].value = 0
                self.outputs[0].type = "float"
                return False

    def add(self, input_edges):
        return input_edges[0].value + input_edges[1].value

    def substract(self, input_edges):
        return input_edges[0].value - input_edges[1].value

    def multiply(self, input_edges):
        return input_edges[0].value * input_edges[1].value

    def devide(self, input_edges):
        return input_edges[0].value / input_edges[1].value

    def power(self, input_edges):
        return pow(input_edges[0].value, input_edges[1].value)










class ExpressionGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 250.0
        self.height = 120.0

class ExpressionContent(DataContent):

    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,0,0,0)
        self.setLayout(self.layout)
        self.edit = QLineEdit("2+2", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.edit)


    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_EXPRESSION)
class ExpressionNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_EXPRESSION
    op_title = "Expression"

    def __init__(self, scene, inputs=[1,1,1], outputs=[2], innames=["a", "b", "c"]):
        super().__init__(scene, inputs, outputs, innames)
        self.x = None
        self.setDirty(False)
        self.setDescendentsDirty(False)
        self.outputs[0].value = 4
        self.outputs[0].type  = "float"

    def initInnerClasses(self):
        self.content = ExpressionContent(self)
        self.grNode  = ExpressionGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        input_a = self.getInput(0)
        input_b = self.getInput(1)
        input_c = self.getInput(2)
        
        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            a = 0
            b = 0
            c = 0
            if input_a:
                a = input_a.value
                if input_a.type == "float":
                    a   = float(a)
                else:
                    a = np.array(a)

            if input_b:
                b = input_b.value
                if input_b.type == "float":
                    b   = float(b)
                else:
                    b = np.array(b)

            if input_c:
                c = input_c.value
                if input_c.type == "float":
                    c   = float(c)
                else:
                    c = np.array(c)

            res = eval(self.content.edit.text(), {"a":a, "b":b, "c":c})

            self.outputs[0].value = res
            self.outputs[0].type  = "float"
            return True
        except Exception as e : 
            dumpException(e)
            return False