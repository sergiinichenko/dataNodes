
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import numpy as np
from math import *

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
                values = [input_edges[0].copy(), input_edges[1].copy()]
                if self.content.operation == "Add"      : self.getOutput(0).value = {name : self.add(values)}
                if self.content.operation == "Substract": self.getOutput(0).value = {name : self.substract(values)}
                if self.content.operation == "Multiply" : self.getOutput(0).value = {name : self.multiply(values)}
                if self.content.operation == "Divide"   : self.getOutput(0).value = {name : self.devide(values)}
                if self.content.operation == "Power"    : self.getOutput(0).value = {name : self.power(values)}
                self.getOutput(0).type = "df"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not all input nodes are connected"
                name = self.content.label.text()
                self.getOutput(0).value = {name : 0.0}
                self.getOutput(0).type = "df"
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
            name = list(input.value.keys())[0]
            input.value[name] = np.nan_to_num(input.value[name])
            return input.value[name]
        if isinstance(input.value, float) or isinstance(input.value, int):
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










class ExpressionGraphicsNode(ResizableInputGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.min_height = 100.0
        self.width  = 260.0
        self.height = 100.0

class ExpressionContent(ResizableInputContent):
    def initUI(self):
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(40,0,0,0)

        self.hlayout = QHBoxLayout()
        self.vlayout = QHBoxLayout()
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addLayout(self.vlayout)

        self.label_name = QLabel("", self)        
        self.label_name.setAlignment(Qt.AlignRight)

        self.label = QLineEdit("res", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(60)
        self.hlayout.addWidget(self.label_name)
        self.hlayout.addWidget(self.label)


        self.edit = QLineEdit("2+2", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.vlayout.addWidget(self.edit)
        self.mainlayout.addStretch()

        self.setLayout(self.mainlayout)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        res['label'] = self.label.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.label.setText(data['label'])
            self.edit.setText( data['value'])
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_EXPRESSION)
class ExpressionNode(ResizableInputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_EXPRESSION
    op_title = "Expression"

    def __init__(self, scene, inputs=[1], outputs=[2]):
        super().__init__(scene, inputs, outputs)
        self.setDirty(False)
        self.setDescendentsDirty(False)
        self.getOutput(0).value = 4
        self.getOutput(0).type  = "float"

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = ExpressionContent(self)
        self.grNode  = ExpressionGraphicsNode(self)
        self.content.edit.returnPressed.connect(self.recalculate)
        self.content.label.returnPressed.connect(self.recalculate)
        self.content.changed.connect(self.recalculate)
    
    def recalculate(self):
        self.setDirty()
        self.eval()

    def evalImplementation(self):
        inputs = self.getInputs()
        if not inputs:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            self.getSocketsNames()
            self.generateNewSocket()
            try:
                label = self.content.label.text()
                expression = self.content.edit.text()
                methods = {'exp' : np.exp, 'pow': np.power, 'log':np.log, 
                           'cos' : np.cos, 'sin': np.sin, 'abs':np.abs,
                           'max' : np.max, 'min': np.min, 'sum':np.sum}

                code = compile(expression, "<string>", "eval")

                if len(inputs) > 0:      
                    self.setDirty(False)
                    self.setInvalid(False)
                    self.e = ""
                    self.value = {}
                    self.filtered = {}
                    for input in inputs[:-1]:
                        for name in input.value:
                            self.filtered[name] = np.nan_to_num(input.value[name])

                    res = eval(code, self.filtered, methods)
                    self.getOutput(0).value = {label : res}
                    self.getOutput(0).type  = "df"
                    return True

                else:
                    res = eval(code, methods)
                    self.getOutput(0).value = {label : res}
                    self.getOutput(0).type  = "float"
                    return True
            
            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = e
                self.getOutput(0).value = {label : 0.0}
                self.getOutput(0).type = "float"
                return False
