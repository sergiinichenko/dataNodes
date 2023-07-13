
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QPlainTextEdit, QLineEdit, QLabel, QComboBox, QHBoxLayout
import numpy as np
import sys
import re
import threading
#from math import *
import copy

class MathGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 150
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
        self.cb.addItem("Rand.uniform")
        self.cb.addItem("Rand.normal")
        self.cb.insertSeparator(13)
        self.cb.addItem("log")
        self.cb.addItem("log10")
        self.cb.addItem("exp")

        #self.cb.insertSeparator(17)
        #self.cb.addItem("Differentiate")
        #self.cb.addItem("Integrate")

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
        self.content.label.returnPressed.connect(self.recalculateNode)
        self.content.valuex.returnPressed.connect(self.recalculateNode)
        self.content.valuey.returnPressed.connect(self.recalculateNode)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin   = 24
        self.socket_spacing         = 23

    def updateInputSockets(self):
        pass

    def checkTheInputs(self):
        if self.hasInput(0):
            self.content.valuey.setReadOnly(True)
            self.content.valuey.setStyleSheet("color: rgba(255, 255, 255, 0.2);")
        else:
            self.content.valuey.setReadOnly(False)
            self.content.valuey.setStyleSheet("color: rgba(255, 255, 255, 1.0);")

        if self.hasInput(1):
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
            self.e      = ""
            self.label  = self.content.label.text()
            if_inpx = self.hasInput(1)
            if_inpy = self.hasInput(0)
            
            if self.getInput(1): valuex = self.getInput(1).value
            else:                valuex = {"x" : [float(self.content.valuex.text())]}

            if self.getInput(0): valuey = self.getInput(0).value
            else:                valuey = {"y" : [float(self.content.valuey.text())]}

            self.value = {}
            res        = {}
            if self.content.operation == "Add"           : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.add)
            if self.content.operation == "Substract"     : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.substract)
            if self.content.operation == "Multiply"      : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.multiply)
            if self.content.operation == "Divide"        : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.devide)
            if self.content.operation == "Power"         : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.power)
            if self.content.operation == "Distance"      : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.distance)
            if self.content.operation == "log"           : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.log)
            if self.content.operation == "log10"         : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.log10)
            if self.content.operation == "exp"           : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.exp)
            if self.content.operation == "Rand.uniform"  : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.randomize_unif)
            if self.content.operation == "Rand.normal"   : res = self.perform(valuex, valuey, if_inpx, if_inpy, self.randomize_norm)
            if self.content.operation == "Sum"        : 
                for name in valuex : res[name] = valuex[name]
                for name in valuey : res[name] = valuey[name]
                for key in res.keys() : res[key] = sum(res[key])

            if self.content.operation == "Absolute"   : 
                for name in valuex : res[name] = valuex[name]
                for name in valuey : res[name] = valuey[name]
                for key in res.keys() : res[key] = [abs(ele) for ele in res[key]]

            if self.content.operation == "Normalize"   : 
                for name in valuex : res[name] = valuex[name]
                for name in valuey : res[name] = valuey[name]
                for key in res.keys() : res[key] = [v/sum(res[key]) for v in res[key]]

            """
            if self.content.operation == "Sum"           : res = self.sum(values)
            if self.content.operation == "Absolute"      : res = self.absolute(values)
            if self.content.operation == "Normalize"     : res = self.normilize(values)
            if self.content.operation == "Differentiate" : res = self.differentiate(values)
            if self.content.operation == "Integrate"     : res = self.integrate(values)
            """
            if len(res) > 1:
                self.getOutput(0).value = res
            else:
                self.value[self.label]  = res[list(res.keys())[0]]
                self.getOutput(0).value = self.value
            
            #self.getOutput(0).value = res
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

    def perform(self, valuex, valuey, if_inpx, if_inpy, operation):
        res = {}
        
        namex_key   = list(valuex.keys())
        namey_key   = list(valuey.keys())
        namesx_size = len(namex_key)
        namesy_size = len(namey_key)
        name_size   = max(namesx_size, namesy_size) 
        namex_i = 0
        namey_i = 0

        names_out = namey_key
        if namesx_size > namesy_size:
            names_out = namex_key
            
        for name_i in range(name_size):
            namex = namex_key[namex_i]
            namey = namey_key[namey_i]
            name  = names_out[name_i]

            sizex = len(valuex[namex])
            sizey = len(valuey[namey])
            size  = max(sizex, sizey)
            i = 0
            j = 0
            res[name] = []
            #if np.any(np.isreal(valuex[namex])==False) or np.any(np.isreal(valuey[namey])==False):
            #    res[name].extend([operation(valuex[namex][i], valuey[namey][j])])
            #    continue
            for count in range(size):
                res[name].extend([operation(valuex[namex][i], valuey[namey][j])])
                i+=1
                j+=1
                if i >= sizex : i = 0
                if j >= sizey : j = 0
            namex_i+=1
            namey_i+=1
            if namex_i >= namesx_size : namex_i = 0
            if namey_i >= namesy_size : namey_i = 0

        return res

    def add(self, x, y):
        return x + y

    def substract(self, x, y):
        return x - y

    def multiply(self, x, y):
        return x * y

    def devide(self, x, y):
        return x / y


    def power(self, x, y):
        return x ** y

    def log(self, x, y):
        return np.log(y)

    def log10(self, x, y):
        return np.log10(y)

    def exp(self, x, y):
        return np.exp(y)

    def randomize_unif(self, x, y):
        return x + np.random.rand() * y

    def randomize_norm(self, x, y):
        return np.random.normal(loc = x, scale = y)

    def distance(self, x, y):
        return abs(x - y)

    def absolute(self, x, y):
        return abs(x - y)

    def normilize(self, input_values):
        res = {}
        for i in input_values[0]:
            res[i] = self.drop_nan(input_values[0][i]) / np.sum(self.drop_nan(input_values[0][i]))
        for j in input_values[1]:
            res[j] = self.drop_nan(input_values[1][j]) / np.sum(self.drop_nan(input_values[1][j]))
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
        self.min_height = 100
        self.width  = 260
        self.height = 100

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
        self.content.label.returnPressed.connect(self.recalculateNode)
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










import traceback

class InterpreterError(Exception): pass

class WorkingThread(QThread):
    work_done = pyqtSignal(object)
    error     = pyqtSignal(str)
    name      = "name"
    code      = "codes"
    inputs    = "inputs"
    variables = "variables"
    filtered  = "filtered"
    locals    = "locals"
    
    def __init__(self):
        QThread.__init__(self)
    
    def setData(self, name, codes, inputs, variables, filtered, locals):
        self.name      = name
        self.code      = codes
        self.inputs    = inputs
        self.variables = variables
        self.filtered  = filtered
        self.locals    = locals
    
    def run(self):
        try:
            print("21")
            exec(self.code, self.filtered, self.locals)
            self.work_done.emit((True, self.inputs, self.filtered, self.variables, self.locals))
            print("22")
        except:
            self.work_done.emit((False, self.inputs, self.filtered, self.variables, self.locals))
            print("23")

class TextField(QPlainTextEdit):
    def __init__(self, content = None):
        super().__init__()
        self.content = content
        #self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.setPlainText("x = 2 + 2")

    def initUI(self):
        self.installEventFilter(self)

    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == Qt.Key_Return and qKeyEvent.modifiers() & Qt.ShiftModifier:
            self.content.node.recalculateNode()
            return
        super().keyPressEvent(qKeyEvent)


class CodeGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.min_height = 200
        self.min_width  = 160
        self.width   = 350
        self.height  = 260
        
class CodeContent(DataContent):
    def initUI(self):

        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(40,5,5,5)

        self.hlayout = QHBoxLayout()
        self.vlayout = QHBoxLayout()
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addLayout(self.vlayout)

        self.edit = TextField(self)
        self.vlayout.addWidget(self.edit)
        
        self.setLayout(self.mainlayout)


    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.toPlainText()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.edit.setPlainText( data['value'])
            if 'height' in data: self.node.grNode.height = data['height']
            if 'width'  in data: self.node.grNode.width  = data['width']
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_CODEBLOCK)
class CodeNode(ResizableInputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_CODEBLOCK
    op_title = "Code block"

    def __init__(self, scene, inputs=[1], outputs=[2]):
        super().__init__(scene, inputs, outputs)
        self.setDirty(False)
        self.setDescendentsDirty(False)
        self.getOutput(0).value = 4
        self.getOutput(0).type  = "float"
        self.event = threading.Event()
        self.thread = WorkingThread()

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content    = CodeContent(self)
        self.grNode     = CodeGraphicsNode(self)
        self.properties = NodeProperties(self)
        #self.content.edit.returnPressed.connect(self.recalculateNode)
        self.content.changed.connect(self.recalculateNode)

    def run(self, code, filtered, locals):
        try:
            exec(code, filtered, locals)
        except Exception as e:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = e
            self.getOutput(0).value = {"res" : 0.0}
            self.getOutput(0).type = "float"
        self.event.set()
    
    def retreiveResults(self, data):
        res, inputs, filtered, variables, locals = data[0], data[1], data[2], data[3], data[4]
        if not res :
            self.setBusy(False)
            self.setDirty(False)
            self.setInvalid(True)
            self.e = "Some problem wiht the data"
            self.setDescendentsInvalid()
            return

        for var in variables:
            if var in locals:
                self.value[var] = locals[var]

        for input in inputs[:-1]:
            for name in input.value: 
                self.value[name] = filtered[name]

        self.getOutput(0).value = self.value
        self.getOutput(0).type  = "df"   
        self.setBusy(False)
        self.setDirty(False)
        self.setInvalid(False)
        self.e = ""
        self.setDescendentsInvalid(False)
        self.setDescendentsDirty()
        self.evalChildren()

    def print_error(self, message):
        print("77")
        print(message)

    def evalImplementation(self, silent=False):
        inputs = self.getInputs()
        self.value = {}
        if not inputs:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            try:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = {}
                self.filtered = {}   
                
                os.chdir(self.scene.path)
                if self.scene.path not in sys.path:
                    sys.path.insert(0, self.scene.path)

                expression = self.content.edit.toPlainText()
                localVars = {'exp' : np.exp, 'pow': np.power, 'log':np.log, 'log10':np.log10,   
                             'cos' : np.cos, 'sin': np.sin, 'abs':np.abs, 'sqrt':np.sqrt,
                             'max' : np.max, 'min': np.min, 'sum':np.sum, 'PI':np.pi, 'pi':np.pi}

                code = compile(expression, "<string>", "exec")
                
                
                if len(inputs) > 0:      
                    for input in inputs[:-1]:
                        for name in input.value:
                            self.filtered[name] = np.nan_to_num(input.value[name])

                variables = []
                for l in iter(expression.splitlines()):
                    if "=" in l:
                        tmp = l.split("=")[0].replace(" ","")
                        if tmp.isalnum():
                            variables.append(tmp)

                #exec(code, self.filtered, localVars)
                self.setBusy(True)
                #thread    = threading.Thread(name='Calculations', target=self.run, args=(code, self.filtered, localVars), daemon=True)
                self.thread.setData(name='Calculations', codes=code, inputs=self.inputs,variables=variables, filtered=self.filtered, locals=localVars)
                self.thread.work_done.connect(self.retreiveResults)
                self.thread.error.connect(self.print_error)
                self.thread.start()
                """
                for input in inputs[:-1]:
                    for name in input.value: 
                        self.value[name] = self.filtered[name]

                for var in variables:
                    if var in localVars : self.value[var] = localVars[var]
                """                 
                return True
            
            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                print(e)
                self.e = e
                #self.getOutput(0).value = {"res" : 0.0}
                #self.getOutput(0).type = "float"
                return False
