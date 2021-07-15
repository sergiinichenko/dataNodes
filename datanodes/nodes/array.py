
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from datanodes.core.utils import *

class StepRangeGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140.0
        self.height = 160.0

class StepRangeContent(DataContent):

    def initUI(self):
        super().initUI()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.name = QLineEdit("res", self)
        self.name.setAlignment(Qt.AlignCenter)
        self.label_name = QLabel("Name", self)        
        self.label_name.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.name, 0, 1)

        self.start = QLineEdit("0", self)
        self.start.setAlignment(Qt.AlignCenter)
        self.label_start = QLabel("Start", self)        
        self.label_start.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_start, 1, 0)
        self.layout.addWidget(self.start, 1, 1)

        self.step = QLineEdit("0.1", self)
        self.step.setAlignment(Qt.AlignCenter)
        self.label_step = QLabel("Start", self)        
        self.label_step.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_step, 2, 0)
        self.layout.addWidget(self.step, 2, 1)

        self.stop = QLineEdit("1", self)
        self.stop.setAlignment(Qt.AlignCenter)
        self.label_stop = QLabel("Stop", self)        
        self.label_stop.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_stop, 3, 0)
        self.layout.addWidget(self.stop, 3, 1)


    def serialize(self):
        res = super().serialize()
        res['name']  = self.name.text()
        res['start'] = self.start.text()
        res['step']  = self.step.text()
        res['stop']  = self.stop.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.name.setText( data['name'])
            self.start.setText(data['start'])
            self.step.setText( data['step'])
            self.stop.setText( data['stop'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_STEPARR)
class StepRangeNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_STEPARR
    op_title = "Array Step"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs, outputs)
        self.eval()

    def initInnerClasses(self):
        self.content = StepRangeContent(self)
        self.grNode  = StepRangeGraphicsNode(self)
        self.content.name.textChanged.connect(self.onReturnPressed)
        self.content.start.textChanged.connect(self.onReturnPressed)
        self.content.step.textChanged.connect(self.onReturnPressed)
        self.content.stop.textChanged.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.recalculate = True
        self.eval()

    def evalImplementation(self):
        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            name  = self.content.name.text()
            start = float(self.content.start.text())
            step  = float(self.content.step.text())
            stop  = float(self.content.stop.text())

            self.getOutput(0).value = { name : np.arange(start, stop+step, step) }
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False







class NumRangeGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 145.0
        self.height = 150.0

class NumRangeContent(DataContent):

    def initUI(self):
        super().initUI()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.name = QLineEdit("res", self)
        self.name.setAlignment(Qt.AlignCenter)
        self.label_name = QLabel("Name", self)        
        self.label_name.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.name, 0, 1)

        self.start = QLineEdit("0", self)
        self.start.setAlignment(Qt.AlignCenter)
        self.label_start = QLabel("Start", self)        
        self.label_start.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_start, 1, 0)
        self.layout.addWidget(self.start, 1, 1)

        self.number = QLineEdit("10", self)
        self.number.setAlignment(Qt.AlignCenter)
        self.label_number = QLabel("Number", self)        
        self.label_number.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_number, 2, 0)
        self.layout.addWidget(self.number, 2, 1)

        self.stop = QLineEdit("1", self)
        self.stop.setAlignment(Qt.AlignCenter)
        self.label_stop = QLabel("Stop", self)        
        self.label_stop.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_stop, 3, 0)
        self.layout.addWidget(self.stop, 3, 1)


    def serialize(self):
        res = super().serialize()
        res['name']  = self.name.text()
        res['start'] = self.start.text()
        res['number']  = self.number.text()
        res['stop']  = self.stop.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.name.setText( data['name'])
            self.start.setText(data['start'])
            self.number.setText( data['number'])
            self.stop.setText( data['stop'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_NUMPARR)
class NumRangeNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_NUMPARR
    op_title = "Array Number"

    def __init__(self, scene, inputs=[1,1,1], outputs=[2]):
        super().__init__(scene, inputs, outputs)
        self.eval()

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_spacing = 30.0
        self.socket_bottom_margin = 22.0


    def initInnerClasses(self):
        self.content = NumRangeContent(self)
        self.grNode  = NumRangeGraphicsNode(self)
        self.content.name.textChanged.connect(self.onContentChanged)
        self.content.start.textChanged.connect(self.onContentChanged)
        self.content.number.textChanged.connect(self.onContentChanged)
        self.content.stop.textChanged.connect(self.onContentChanged)
        self.content.changed.connect(self.onContentChanged)

    def onContentChanged(self):
        self.recalculate = True
        self.eval()

    def checkTheInputs(self):
        if self.getInput(0) is not None:
            self.content.start.setReadOnly(True)
        else:
            self.content.start.setReadOnly(False)

        if self.getInput(1) is not None:
            self.content.number.setReadOnly(True)
        else:
            self.content.number.setReadOnly(False)

        if self.getInput(2) is not None:
            self.content.stop.setReadOnly(True)
        else:
            self.content.stop.setReadOnly(False)

    def evalImplementation(self):
        try:
            self.checkTheInputs()
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            name  = self.content.name.text()
            if self.getInput(2) is not None:
                val = self.getInput(2).value
                start = float(self.content.start.text())
                if isinstance(val, dict):
                    start = list(val.values())[0]
                if isinstance(val, float):
                    start = val
                if isinstance(val, (list, np.ndarray)):
                    start = val[0]
                self.content.start.setText("{:.2f}".format(start))
            else:
                start = float(self.content.start.text())

            if self.getInput(1) is not None:
                val = self.getInput(1).value
                num = int(self.content.number.text())
                if isinstance(val, dict):
                    num = lenOfDictValue(val)
                if isinstance(val, float):
                    num = int(val)
                if isinstance(val, int):
                    num = val
                if isinstance(val, (list, np.ndarray)):
                    num = len(val)
                self.content.number.setText(str(int(num)))
            else:
                num = int(self.content.number.text())

            if self.getInput(0) is not None:
                val = self.getInput(0).value
                stop = float(self.content.stop.text())
                if isinstance(val, dict):
                    stop = list(val.values())[0]
                if isinstance(val, float):
                    stop = val
                if isinstance(val, (list, np.ndarray)):
                    stop = val[0]
                self.content.stop.setText("{:.2f}".format(stop))
            else:
                stop = float(self.content.stop.text())

            self.getOutput(0).value =  { name : np.linspace(start, stop, num) }
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False            








class FilledArrayGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140.0
        self.height = 160.0

class FilledArrayContent(DataContent):

    def initUI(self):
        super().initUI()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.name = QLineEdit("res", self)
        self.name.setAlignment(Qt.AlignCenter)
        self.label_name = QLabel("Name", self)        
        self.label_name.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.name, 0, 1)

        self.number = QLineEdit("10", self)
        self.number.setAlignment(Qt.AlignCenter)
        self.label_number = QLabel("Number", self)        
        self.label_number.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_number, 2, 0)
        self.layout.addWidget(self.number, 2, 1)

        self.value = QLineEdit("1", self)
        self.value.setAlignment(Qt.AlignCenter)
        self.label_value = QLabel("Value", self)        
        self.label_value.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.label_value, 3, 0)
        self.layout.addWidget(self.value, 3, 1)


    def serialize(self):
        res = super().serialize()
        res['name']   = self.name.text()
        res['number'] = self.number.text()
        res['value']  = self.value.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.name.setText( data['name'])
            self.number.setText( data['number'])
            self.value.setText( data['value'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_FILLPARR)
class FilledArrayNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_FILLPARR
    op_title = "Array Filled"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs, outputs)
        self.eval()

    def initInnerClasses(self):
        self.content = FilledArrayContent(self)
        self.grNode  = FilledArrayGraphicsNode(self)
        self.content.name.textChanged.connect(self.onReturnPressed)
        self.content.number.textChanged.connect(self.onReturnPressed)
        self.content.value.textChanged.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.recalculate = True
        self.eval()

    def evalImplementation(self):
        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            name  = self.content.name.text()
            shape = int(self.content.number.text())
            value = float(self.content.value.text())

            self.getOutput(0).value =  { name : np.full(shape, value) }
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False                        