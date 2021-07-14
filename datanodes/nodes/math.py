
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class MathGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 160.0

class MathContent(DataContent):

    def initUI(self):
        super().initUI()
        self.operation = "Add"
        self.layout = QVBoxLayout()
        self.cb = QComboBox()
        self.cb.addItem("Add")
        self.cb.addItem("Substract")
        self.cb.addItem("Multiply")
        self.cb.addItem("Divide")
        self.cb.addItem("Power")

        self.label = QLineEdit("res", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.cb)
        self.setLayout(self.layout)
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
        self.content.label.returnPressed.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.recalculate = True
        self.eval()

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
                name = self.content.label.text()
                if self.content.operation == "Add"      : self.outputs[0].value = {name : self.add(input_edges)}
                if self.content.operation == "Substract": self.outputs[0].value = {name : self.substract(input_edges)}
                if self.content.operation == "Multiply" : self.outputs[0].value = {name : self.multiply(input_edges)}
                if self.content.operation == "Divide"   : self.outputs[0].value = {name : self.devide(input_edges)}
                if self.content.operation == "Power"    : self.outputs[0].value = {name : self.power(input_edges)}
                self.outputs[0].type = "df"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not all input nodes are connected"
                name = self.content.label.text()
                self.outputs[0].value = {name : 0.0}
                self.outputs[0].type = "df"
                return False

    def drop_nan(self, input):

        if isinstance(input.value, pd.DataFrame):
            return input.value.replace(np.nan, 0)
        if isinstance(input.value, pd.Series):
            return input.value.replace(np.nan, 0)
        if isinstance(input.value, (np.ndarray, np.generic)):
            val = input.value[np.isnan(input.value)] = 0.0
            return val 
        if isinstance(input.value, dict):
            val = input.value[np.isnan(input.value)] = 0.0
            return val 
        return input.value

    def add(self, input_edges):
        return self.drop_nan(input_edges[0]) + self.drop_nan(input_edges[1])

    def substract(self, input_edges):
        return self.drop_nan(input_edges[0]) - self.drop_nan(input_edges[1])

    def multiply(self, input_edges):
        return self.drop_nan(input_edges[0]) * self.drop_nan(input_edges[1])

    def devide(self, input_edges):
        return self.drop_nan(input_edges[0]) / self.drop_nan(input_edges[1])

    def power(self, input_edges):
        return pow(self.drop_nan(input_edges[0]), self.drop_nan(input_edges[1]))










class ExpressionGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 250.0
        self.height = 120.0

class ExpressionContent(DataContent):

    def initUI(self):
        super().initUI()
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(20,0,0,0)

        self.hlayout = QHBoxLayout()
        self.vlayout = QHBoxLayout()
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addLayout(self.vlayout)

        self.label_name = QLabel("result", self)        
        self.label_name.setAlignment(Qt.AlignRight)

        self.label = QLineEdit("res", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(60)
        self.hlayout.addWidget(self.label_name)
        self.hlayout.addWidget(self.label)


        self.edit = QLineEdit("2+2", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.vlayout.addWidget(self.edit)

        self.setLayout(self.mainlayout)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        res['label'] = self.label.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.label.setText(data['label'])
            self.edit.setText( data['value'])
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

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = ExpressionContent(self)
        self.grNode  = ExpressionGraphicsNode(self)
        self.content.edit.returnPressed.connect(self.onReturnPressed)
        self.content.label.returnPressed.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.recalculate = True
        self.eval()

    def evalImplementation(self):
        input_a = self.getInput(0)
        input_b = self.getInput(1)
        input_c = self.getInput(2)

        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            name = self.content.label.text()
            a = 0
            b = 0
            c = 0
            if input_a:
                a = input_a.value[np.isnan(input_a.value)] = 0.0
                if input_a.type == "float":
                    a   = float(a)
                else:
                    a = np.array(a)

            if input_b:
                b = input_b.value[np.isnan(input_b.value)] = 0.0
                if input_b.type == "float":
                    b   = float(b)
                else:
                    b = np.array(b)

            if input_c:
                c = input_c.value[np.isnan(input_c.value)] = 0.0
                if input_c.type == "float":
                    c   = float(c)
                else:
                    c = np.array(c)

            if not input_a and not input_b and not input_c:
                self.outputs[0].value = {name : [0.0]}
                self.outputs[0].type  = "float"
                return True
            
            expression = self.content.edit.text()
            expression = expression.replace('exp', '2.71828182845904523536028747**')
            res = eval(expression, {"a":a, "b":b, "c":c})

            self.outputs[0].value = {name : res}
            self.outputs[0].type  = "float"
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False