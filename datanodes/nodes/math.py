
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import numpy as np
from math import *
import copy

class MathGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 150.0
        self.setZValue(5)

class MathContent(DataContent):

    def initUI(self):
        super().initUI()
        self.setWindowTitle("Math node")

        self.operation = "Add"

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.label_name = QLabel("", self)        
        self.label_name.setAlignment(Qt.AlignRight)
        self.label = QLineEdit("res", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(60)
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.label, 0, 1)

        self.cb = QComboBox()
        self.cb.addItem("Add")
        self.cb.addItem("Substract")
        self.cb.addItem("Multiply")
        self.cb.addItem("Divide")
        self.cb.addItem("Power")
        self.cb.insertSeparator(5)
        self.cb.addItem("Distance")
        self.cb.addItem("Sum")
        self.cb.addItem("Absolute")
        self.cb.addItem("Normalize")
        self.cb.insertSeparator(10)
        self.cb.addItem("Randomize")
        self.cb.insertSeparator(12)
        self.cb.addItem("Differentiate")
        self.cb.addItem("Integrate")

        self.cb.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(self.cb, 1, 0, 1, 2)
        self.cb.currentIndexChanged.connect(self.selectionchange)

        self.valuex = QLineEdit("1.0", self)
        self.valuex.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.valuex, 2, 0, 1, 2)

        self.valuey = QLineEdit("1.0", self)
        self.valuey.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.valuey, 3, 0, 1, 2)

    def selectionchange(self,i):
        self.operation = self.cb.currentText()
        self.changed.emit()

    def serialize(self):
        res = super().serialize()
        res['sel_ind'] = self.cb.currentIndex()
        res['label']   = self.label.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.cb.setCurrentIndex(data['sel_ind'])
            self.label.setText(data['label'])
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
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)
        self.content.label.textChanged.connect(self.recalculateNode)
        self.content.valuex.textChanged.connect(self.recalculateNode)
        self.content.valuey.textChanged.connect(self.recalculateNode)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin   = 24
        self.socket_spacing         = 23

    def checkTheInputs(self):
        if self.getInput(0) is not None:
            self.content.valuey.setReadOnly(True)
            self.content.valuey.setStyleSheet("color: rgba(255, 255, 255, 0.2);")
        else:
            self.content.valuey.setReadOnly(False)
            self.content.valuey.setStyleSheet("color: rgba(255, 255, 255, 1.0);")

        if self.getInput(1) is not None:
            self.content.valuex.setReadOnly(True)
            self.content.valuex.setStyleSheet("color: rgba(255, 255, 255, 0.2);")
        else:
            self.content.valuex.setReadOnly(False)
            self.content.valuex.setStyleSheet("color: rgba(255, 255, 255, 1.0);")


    def evalImplementation(self, silent=False):
        try:
            self.checkTheInputs()
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""

            if self.getInput(1): valuex = self.getInput(1).value
            else:                valuex = float(self.content.valuex.text())

            if self.getInput(0): valuey = self.getInput(0).value
            else:                valuey = float(self.content.valuey.text())

            res = {}
            if self.content.operation == "Add"           : res = self.add(valuex, valuey)
            if self.content.operation == "Substract"     : res = self.substract(valuex, valuey)
            if self.content.operation == "Multiply"      : res = self.multiply(valuex, valuey)
            if self.content.operation == "Divide"        : res = self.devide(valuex, valuey)
            if self.content.operation == "Power"         : res = self.power(valuex, valuey)
            if self.content.operation == "Distance"      : res = self.distance(valuex, valuey)
            """
            if self.content.operation == "Sum"           : res = self.sum(values)
            if self.content.operation == "Absolute"      : res = self.absolute(values)
            if self.content.operation == "Normalize"     : res = self.normilize(values)
            if self.content.operation == "Randomize"     : res = self.randomize(values)
            if self.content.operation == "Differentiate" : res = self.differentiate(values)
            if self.content.operation == "Integrate"     : res = self.integrate(values)
            if len(res) > 1:
                self.getOutput(0).value = res
            else:
                self.getOutput(0).value = {label : res[list(res.keys())[0]]}
            """
            
            self.getOutput(0).value = res
            self.getOutput(0).type  = "df"
            return True
        except Exception as e:
            self.setInvalid()
            self.e = e
            self.getOutput(0).value = {"x" : 0.0}
            self.getOutput(0).type = "df"
            return False


    def drop_nan(self, input_value):
        
        if isinstance(input_value, pd.DataFrame):
            return input_value.replace(np.nan, 0)

        if isinstance(input_value, pd.Series):
            return input_value.replace(np.nan, 0)

        if isinstance(input_value, (np.ndarray, np.generic)):
            input_value[np.isnan(input_value)] = 0.0
            return input_value

        if isinstance(input_value, dict):
            for name in input_value:
                name = list(input_value.keys())[0]
                input_value[name] = np.nan_to_num(input_value[name])
            return input_value

        if isinstance(input_value, float) or isinstance(input_value, int):
            return input_value

    def singleValue(self, value):
        if isinstance(value, float) or isinstance(value, int):
            return True, value

        if isinstance(value, (np.ndarray, np.generic)):
            value.size() == 1
            return True, value[0]

        if isinstance(value, dict):
            if len(value) == 1:
                if len(list(value.values())) == 1:
                    return True, list(value.values())[0]
        return False, value

    def add(self, valuex, valuey):
        res = {}
        valx_s, valx = self.singleValue(valuex)
        valy_s, valy = self.singleValue(valuey)

        if valx_s and valy_s:
            return {"x": valx + valy}

        elif valx_s:
            for name in valuey:
                res[name] = valx + self.drop_nan(valuey[name])

        elif valy_s:
            for name in valuex:
                res[name] = valy + self.drop_nan(valuex[name])

        else:
            for i, j in zip(valuex, valuey):
                res[j] = self.drop_nan(valuex[i]) + self.drop_nan(valuey[j])
        return res

    def substract(self, valuex, valuey):
        res = {}
        valx_s, valx = self.singleValue(valuex)
        valy_s, valy = self.singleValue(valuey)

        if valx_s and valy_s:
            return {"x": valx - valy}

        elif valx_s:
            for name in valuey:
                res[name] = valx - self.drop_nan(valuey[name])

        elif valy_s:
            for name in valuex:
                res[name] = (-1.0)*valy + self.drop_nan(valuex[name])

        else:
            for i, j in zip(valuex, valuey):
                res[j] = self.drop_nan(valuex[i]) - self.drop_nan(valuey[j])
        return res


    def multiply(self, valuex, valuey):
        res = {}
        valx_s, valx = self.singleValue(valuex)
        valy_s, valy = self.singleValue(valuey)

        if valx_s and valy_s:
            return {"x": valx * valy}

        elif valx_s:
            for name in valuey:
                res[name] = valx * self.drop_nan(valuey[name])

        elif valy_s:
            for name in valuex:
                res[name] = valy * self.drop_nan(valuex[name])

        else:
            for i, j in zip(valuex, valuey):
                res[j] = self.drop_nan(valuex[i]) * self.drop_nan(valuey[j])
        return res


    def devide(self, valuex, valuey):
        res = {}
        valx_s, valx = self.singleValue(valuex)
        valy_s, valy = self.singleValue(valuey)

        if valx_s and valy_s:
            return {"x": valx / valy}

        elif valx_s:
            for name in valuey:
                res[name] = valx / self.drop_nan(valuey[name])

        elif valy_s:
            for name in valuex:
                res[name] = self.drop_nan(valuex[name]) / valy

        else:
            for i, j in zip(valuex, valuey):
                res[j] = self.drop_nan(valuex[i]) / self.drop_nan(valuey[j])
        return res


    def power(self, valuex, valuey):
        res = {}
        valx_s, valx = self.singleValue(valuex)
        valy_s, valy = self.singleValue(valuey)

        if valx_s and valy_s:
            return {"x": valx ** valy}

        elif valx_s:
            for name in valuey:
                res[name] = valx ** self.drop_nan(valuey[name])

        elif valy_s:
            for name in valuex:
                res[name] = self.drop_nan(valuex[name]) ** valy

        else:
            for i, j in zip(valuex, valuey):
                res[j] = self.drop_nan(valuex[i]) ** self.drop_nan(valuey[j])
        return res


    def distance(self, valuex, valuey):
        res = {}
        valx_s, valx = self.singleValue(valuex)
        valy_s, valy = self.singleValue(valuey)

        if valx_s and valy_s:
            return {"x": np.abs(valx - valy)}

        elif valx_s:
            for name in valuey:
                res[name] = np.abs(valx - self.drop_nan(valuey[name]))

        elif valy_s:
            for name in valuex:
                res[name] = np.abs(self.drop_nan(valuex[name]) - valy)

        else:
            for i, j in zip(valuex, valuey):
                res[j] = np.abs(self.drop_nan(valuex[i]) - self.drop_nan(valuey[j]))
        return res


    def sum(self, input_values):
        res = {}
        for i, j in zip(input_values[0], input_values[1]):
            res[i] = np.sum(self.drop_nan(input_values[0][i])) + np.sum(self.drop_nan(input_values[1][j]))
        return res

    def absolute(self, input_values):
        res = {}
        for i in input_values[0]:
            res[i] = np.abs(self.drop_nan(input_values[0][i]))
        for j in input_values[1]:
            res[j] = np.abs(self.drop_nan(input_values[1][j]))
        return res

    def normilize(self, input_values):
        res = {}
        for i in input_values[0]:
            res[i] = self.drop_nan(input_values[0][i]) / np.sum(self.drop_nan(input_values[0][i]))
        for j in input_values[1]:
            res[j] = self.drop_nan(input_values[1][j]) / np.sum(self.drop_nan(input_values[1][j]))
        return res

    def randomize(self, input_values):
        res = {}
        for i, j in zip(input_values[0], input_values[1]):
            rands  = np.random.rand(len(self.drop_nan(input_values[0][i])))
            corrs  = self.drop_nan(input_values[1][j])

            res[i] = self.drop_nan(input_values[0][i]) * (1.0 + corrs * ( rands * 2.0 - 1.0))
        return res

    def cutUp(self, input_values):
        pass

    def cutDown(self, input_values):
        pass


    def differentiate(self, input_values):
        res = {}
        for i, j in zip(input_values[0], input_values[1]):
            res[i] = np.gradient(self.drop_nan(input_values[1][j]), self.drop_nan(input_values[0][i]))
        return res

    def integrate(self, input_values):
        res = {}
        for i, j in zip(input_values[0], input_values[1]):
            res[i] = np.trapz(y=self.drop_nan(input_values[1][j]), x=self.drop_nan(input_values[0][i]))
        return res











class ExpressionGraphicsNode(ResizableGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.min_height = 100.0
        self.width  = 260.0
        self.height = 100.0

class ExpressionContent(ResizableContent):
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

    def __init__(self, scene, inputs=[1], outputs=[2, 1]):
        super().__init__(scene, inputs, outputs)
        self.setDirty(False)
        self.setDescendentsDirty(False)
        self.getOutput(0).value = 4
        self.getOutput(0).type  = "float"
        #self.eval()

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content    = ExpressionContent(self)
        self.grNode     = ExpressionGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.edit.returnPressed.connect(self.recalculateNode)
        self.content.label.returnPressed.connect(self.recalculateNode)
        self.content.label.textChanged.connect(self.recalculateNode)
        self.content.changed.connect(self.recalculateNode)

    def evalImplementation(self, silent=False):
        inputs = self.getInputs()
        self.value = {}
        if not inputs:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            try:
                label = self.content.label.text()
                expression = self.content.edit.text()
                methods = {'exp' : np.exp, 'pow': np.power, 'log':np.log, 
                           'cos' : np.cos, 'sin': np.sin, 'abs':np.abs,
                           'max' : np.max, 'min': np.min, 'sum':np.sum, 'PI':np.pi, 'pi':np.pi}

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
                    for input in inputs[:-1]:
                        for name in input.value: 
                            self.value[name] = self.filtered[name]

                    self.value[label] = res
                    self.getOutput(0).value = {label : res}
                    self.getOutput(0).type  = "df"
                    self.getOutput(1).value = self.value
                    self.getOutput(1).type  = "df"
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
