
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QPlainTextEdit, QLineEdit, QLabel, QComboBox, QHBoxLayout
import numpy as np

class FitGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 220
        self.height = 120
        self.setZValue(5)

class FitContent(DataContent):
    def initUI(self):
        super().initUI()
        self.setWindowTitle("Fit node")

        self.fit_switch = "Linear"

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.cb = QComboBox()
        self.cb.addItem("Linear")
        self.cb.addItem("Power")
        self.cb.addItem("Exponent")
        self.cb.addItem("Logarithm")
        self.cb.insertSeparator(5)
        self.cb.addItem("Poly-2")
        self.cb.addItem("Poly-3")
        self.cb.addItem("Poly-4")
        self.cb.addItem("Poly-5")
        self.cb.addItem("Poly-6")

        self.cb.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(self.cb, 1, 0, 1, 2)
        self.cb.currentIndexChanged.connect(self.selectionchange)

        self.formula = QLineEdit("a + b*x", self)
        self.formula.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.formula, 2, 0, 1, 2)

    def selectionchange(self,i):
        self.fit_switch = self.cb.currentText()
        if self.fit_switch == "Linear"    : self.formula.setText("a + b*x")
        if self.fit_switch == "Power"     : self.formula.setText("a + x^b")
        if self.fit_switch == "Exponent"  : self.formula.setText("a + b*exp(x)")
        if self.fit_switch == "Logarithm" : self.formula.setText("a + b*log(x)")
        if self.fit_switch == "Poly-2"    : self.formula.setText("a + b*x + cx^2")
        if self.fit_switch == "Poly-3"    : self.formula.setText("a + b*x + .. + dx^3")
        if self.fit_switch == "Poly-4"    : self.formula.setText("a + b*x + .. + ex^4")
        if self.fit_switch == "Poly-5"    : self.formula.setText("a + b*x + .. + fx^5")
        if self.fit_switch == "Poly-6"    : self.formula.setText("a + b*x + .. + gx^6")
        self.changed.emit()

    def serialize(self):
        res = super().serialize()
        res['sel_ind'] = self.cb.currentIndex()
        res['formula'] = self.formula.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.cb.setCurrentIndex(data['sel_ind'])
            self.formula.setText(data['formula'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_FIT)
class FitNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_FIT
    op_title = "Fit data"

    def __init__(self, scene, inputs=[1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = FitContent(self)
        self.grNode  = FitGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_bottom_margin   = 24
        self.socket_spacing         = 23

    def updateInputSockets(self):
        pass

    def evalImplementation(self, silent=False):
        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""

            value = self.getInput(0).value
            if not value : 
                self.setInvalid()
                self.e = "No input data"
                return
            
            namex = list(value.keys())[0]
            namey = list(value.keys())[1]
            if len(value[namex]) != len(value[namey]):
                self.setInvalid()
                self.e = "Input data of different size"
                return
            
            res = {}
            if self.content.fit_switch == "Linear"    : res = self.linear(value[namex], value[namey])
            if self.content.fit_switch == "Power"     : res = self.power(value[namex], value[namey])
            if self.content.fit_switch == "Exponent"  : res = self.exponent(value[namex], value[namey])
            if self.content.fit_switch == "Logarithm" : res = self.logarithm(value[namex], value[namey])
            if self.content.fit_switch == "Poly-2"    : res = self.poly_2(value[namex], value[namey])
            if self.content.fit_switch == "Poly-3"    : res = self.poly_3(value[namex], value[namey])
            if self.content.fit_switch == "Poly-4"    : res = self.poly_4(value[namex], value[namey])
            if self.content.fit_switch == "Poly-5"    : res = self.poly_5(value[namex], value[namey])
            if self.content.fit_switch == "Poly-6"    : res = self.poly_6(value[namex], value[namey])
            
            data = value
            data.update({'fit': res})
            
            self.getOutput(0).value = data
            self.getOutput(0).type  = "df"
            return True
        except Exception as e:
            self.setInvalid()
            self.e = e
            self.getOutput(0).value = {"x" : 0.0}
            self.getOutput(0).type = "df"
            return False


    def linear(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(x)

    def power(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(y)

    def exponent(self, x, y):
        z = np.polyfit(x, np.log(y), 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " * exp(" + self.getFormatedValue(np.exp(z[1])) + "x)")
        p = np.poly1d(z)
        return np.exp(p(x))

    def logarithm(self, x, y):
        z = np.polyfit(np.log(x), y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * log(x)")
        p = np.poly1d(z)
        return p(np.log(x))

    def poly_2(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(x)

    def poly_3(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(x)

    def poly_4(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(x)

    def poly_5(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(x)

    def poly_6(self, x, y):
        z = np.polyfit(x, y, 1)
        self.content.formula.setText(self.getFormatedValue(z[0]) + " + " + self.getFormatedValue(z[1]) + " * x")
        p = np.poly1d(z)
        return p(x)





