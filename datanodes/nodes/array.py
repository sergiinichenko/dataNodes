
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from datanodes.core.utils import *
from PyQt5.QtWidgets import QLabel, QGridLayout, QLineEdit

class StepRangeGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140
        self.height = 160

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
        self.label_step = QLabel("Step", self)        
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
    op_title = "Vector (by step)"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = StepRangeContent(self)
        self.grNode  = StepRangeGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.name.returnPressed.connect(self.onReturnPressed)
        self.content.start.returnPressed.connect(self.onReturnPressed)
        self.content.step.returnPressed.connect(self.onReturnPressed)
        self.content.stop.returnPressed.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.recalculate = True
        self.eval()

    def evalImplementation(self, silent=False):
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
        self.height = 140.0

class NumRangeContent(DataContent):

    def initUI(self):
        super().initUI()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
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
    op_title = "Vector (by size)"

    def __init__(self, scene, inputs=[1,1,1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_spacing = 30.0
        self.socket_bottom_margin = 22.0


    def initInnerClasses(self):
        self.content = NumRangeContent(self)
        self.grNode  = NumRangeGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.name.returnPressed.connect(self.onContentChanged)
        self.content.start.returnPressed.connect(self.onContentChanged)
        self.content.number.returnPressed.connect(self.onContentChanged)
        self.content.stop.returnPressed.connect(self.onContentChanged)
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

    def evalImplementation(self, silent=False):
        try:
            self.checkTheInputs()
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            name  = self.content.name.text()

            if self.getInput(2) is not None:
                start = self.getInputVaue(self.getInput(2).value, float(self.content.start.text()))
                self.content.start.setText("{:.2f}".format(start))
            else:
                start = float(self.content.start.text())

            if self.getInput(1) is not None:
                num = int(self.getInputLength(self.getInput(1).value, int(self.content.number.text())))
                self.content.number.setText(str(num))
            else:
                num = int(self.content.number.text())

            if self.getInput(0) is not None:
                stop = self.getInputVaue(self.getInput(0).value, float(self.content.stop.text()))
                self.content.stop.setText("{:.2f}".format(stop))
            else:
                stop = float(self.content.stop.text())

            self.value              =  { name : np.linspace(start, stop, num) }
            self.getOutput(0).value =  self.value
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False            





class FilledArrayGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 145.0
        self.height = 120.0

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
    op_title = "Vector Filled"

    def __init__(self, scene, inputs=[1,1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_spacing = 30.0
        self.socket_bottom_margin = 22.0

    def initInnerClasses(self):
        self.content = FilledArrayContent(self)
        self.grNode  = FilledArrayGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.name.returnPressed.connect(self.onReturnPressed)
        self.content.number.returnPressed.connect(self.onReturnPressed)
        self.content.value.returnPressed.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.recalculate = True
        self.eval()

    def evalImplementation(self, silent=False):
        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            name  = self.content.name.text()

            if self.getInput(1) is not None:
                num = self.getInputLength(self.getInput(1).value, int(self.content.number.text()))
                self.content.number.setText(str(num))
            else:
                num = int(self.content.number.text())

            if self.getInput(0) is not None:
                val = self.getInputVaue(self.getInput(0).value, float(self.content.value.text()))
                self.content.value.setText("{:.2f}".format(val))
            else:
                val = float(self.content.value.text())

            self.getOutput(0).value =  { name : np.full(num, val) }
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False                        









class Mesh2DGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 145.0
        self.height = 156.0

class Mesh2DContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.label_name = QLabel("Name", self)        
        self.label_name.setAlignment(Qt.AlignRight)
        self.name = QLineEdit("m", self)
        self.name.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_name, 0, 0)
        self.layout.addWidget(self.name, 0, 1)


        self.label_sizex = QLabel("Size x", self)        
        self.label_sizex.setAlignment(Qt.AlignRight)
        self.sizex = QLineEdit("10.0", self)
        self.sizex.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_sizex, 1, 0)
        self.layout.addWidget(self.sizex, 1, 1)

        self.label_sizey = QLabel("Size y", self)        
        self.label_sizey.setAlignment(Qt.AlignRight)
        self.sizey = QLineEdit("10.0", self)
        self.sizey.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_sizey, 2, 0)
        self.layout.addWidget(self.sizey, 2, 1)

        self.label_numx = QLabel("Num x", self)        
        self.label_numx.setAlignment(Qt.AlignRight)
        self.numx = QLineEdit("10", self)
        self.numx.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_numx, 3, 0)
        self.layout.addWidget(self.numx, 3, 1)

        self.label_numy = QLabel("Num y", self)        
        self.label_numy.setAlignment(Qt.AlignRight)
        self.numy = QLineEdit("10", self)
        self.numy.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_numy, 4, 0)
        self.layout.addWidget(self.numy, 4, 1)


    def serialize(self):
        res = super().serialize()
        res['sizex']  = self.sizex.text()
        res['sizey']  = self.sizey.text()
        res['numx']   = self.numx.text()
        res['numy']   = self.numy.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.sizex.setText(data['sizex'])
            self.sizey.setText(data['sizey'])
            self.numx.setText(data['numx'] )
            self.numy.setText(data['numy'] )
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_MESH2D)
class Mesh2DNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_MESH2D
    op_title = "Mesh 2D"

    def __init__(self, scene, inputs=[1,1,1,1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_spacing = 24.0
        self.socket_bottom_margin = 0.0
        self.socket_top_margin    = 64.0


    def initInnerClasses(self):
        self.content = Mesh2DContent(self)
        self.grNode  = Mesh2DGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.sizex.returnPressed.connect(self.recalculateNode)
        self.content.sizey.returnPressed.connect(self.recalculateNode)
        self.content.numx.returnPressed.connect(self.recalculateNode)
        self.content.numy.returnPressed.connect(self.recalculateNode)

    def checkTheInputs(self):
        if self.getInput(0) is not None:
            self.content.sizex.setReadOnly(True)
        else:
            self.content.sizex.setReadOnly(False)

        if self.getInput(1) is not None:
            self.content.sizey.setReadOnly(True)
        else:
            self.content.sizey.setReadOnly(False)

        if self.getInput(2) is not None:
            self.content.numx.setReadOnly(True)
        else:
            self.content.numx.setReadOnly(False)

        if self.getInput(3) is not None:
            self.content.numy.setReadOnly(True)
        else:
            self.content.numy.setReadOnly(False)


    def evalImplementation(self, silent=False):
        try:
            self.checkTheInputs()
            name  = self.content.name.text()

            if self.getInput(0) is not None:
                sizex = self.getInputVaue(self.getInput(0).value, float(self.content.sizex.text()))
                self.content.sizex.setText("{:.2f}".format(sizex))
            else:
                sizex = float(self.content.sizex.text())

            if self.getInput(1) is not None:
                sizey = self.getInputVaue(self.getInput(1).value, float(self.content.sizey.text()))
                self.content.sizey.setText(str(sizey))
            else:
                sizey = float(self.content.sizey.text())

            if self.getInput(2) is not None:
                numx = self.getInputVaue(self.getInput(2).value, int(self.content.numx.text()))
                self.content.numx.setText(int(numx))
            else:
                numx = int(self.content.numx.text())

            if self.getInput(3) is not None:
                numy = self.getInputVaue(self.getInput(2).value, int(self.content.numy.text()))
                self.content.numx.setText(int(numy))
            else:
                numy = int(self.content.numy.text())

            x = np.linspace(0, sizex, numx)
            y = np.linspace(0, sizey, numy)
            xv, yv = np.meshgrid(x, y)
            self.getOutput(0).value =  { "x" : xv.flatten(), "y" : yv.flatten() }
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False            











class TernaryGridGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140.0
        self.height = 70.0

class TernaryGridContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.label_size = QLabel("Size", self)        
        self.label_size.setAlignment(Qt.AlignRight)
        self.size = QLineEdit("10", self)
        self.size.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_size, 1, 0)
        self.layout.addWidget(self.size, 1, 1)

    def serialize(self):
        res = super().serialize()
        res['size']  = self.size.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.size.setText(data['size'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_TERNARY_GRID)
class TernaryGridNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_TERNARY_GRID
    op_title = "Grid ternary"

    def __init__(self, scene, inputs=[1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = TernaryGridContent(self)
        self.grNode  = TernaryGridGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.size.returnPressed.connect(self.recalculateNode)


    def checkTheInputs(self):
        if self.getInput(0) is not None:
            self.content.size.setReadOnly(True)
        else:
            self.content.size.setReadOnly(False)

    def evalImplementation(self, silent=False):
        try:
            self.checkTheInputs()

            if self.getInput(0) is not None:
                size = self.getInputVaue(self.getInput(0).value, float(self.content.size.text()))
                self.content.size.setText("{:.2f}".format(size))
            else:
                size = float(self.content.size.text())

            size = int(size)
            step = 1.0 / size

            x = np.empty((0))
            y = np.empty((0))
            z = np.empty((0))

            for i in range(size):
                x = np.append(x, np.linspace(0, 1.0 - step * i, size + 1 - i))
                y = np.append(y, np.full(size + 1 - i, i * step))
            x = np.append(x, [0.0])
            y = np.append(y, [1.0])
            z = 1.0 - x - y

            self.value = { "x" : x, "y" : y, 'z' : z }
            self.getOutput(0).value =  self.value
            return True
        except Exception as e : 
            self.e = e
            dumpException(e)
            return False            
