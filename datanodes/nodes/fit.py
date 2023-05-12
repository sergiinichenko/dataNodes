
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QPlainTextEdit, QLineEdit, QLabel, QComboBox, QHBoxLayout
import numpy as np

class FitGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 120
        self.setZValue(5)

class FitContent(DataContent):
    def initUI(self):
        super().initUI()
        self.setWindowTitle("Fit node")

        self.fit_switch = "Least sqr"

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.cb = QComboBox()
        self.cb.addItem("Least sqr")
        self.cb.addItem("Linear")
        self.cb.addItem("Power")
        self.cb.addItem("Exponent")
        self.cb.addItem("Logarithm")

        self.cb.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(self.cb, 1, 0, 1, 2)
        self.cb.currentIndexChanged.connect(self.selectionchange)

        self.formula = QLineEdit("y = a*x", self)
        self.formula.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.formula, 2, 0, 1, 2)

    def selectionchange(self,i):
        self.fit_switch = self.cb.currentText()
        if self.fit_switch == "Least sqr" : self.formula.setText("a*x")
        if self.fit_switch == "Linear"    : self.formula.setText("a + b*x")
        if self.fit_switch == "Power"     : self.formula.setText("a + x^b")
        if self.fit_switch == "Exponent"  : self.formula.setText("a + b*exp(x)")
        if self.fit_switch == "Logarithm" : self.formula.setText("a + b*log(x)")
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

            self.value = self.getInput(0).value
            if not self.value : 
                self.setInvalid()
                self.e = "No input data"
                return
            
            if len(list(self.value.keys())) < 2:
                self.setInvalid()
                self.e = "No enough input data"
                return

            namey = list(self.value.keys())[0]
            namex = list(self.value.keys())[1:]

            x = np.ones(len(self.value[namex[0]]))
            for name in namex:
                x = np.vstack((x, self.value[name]))
            x = x.T
            y = np.array(self.value[namey])
            
            data = {}
            data.update(self.value)
            if self.content.fit_switch == "Least sqr" : res, coefs = self.lstsq(x[:, 1:], y)
            if self.content.fit_switch == "Linear"    : res, coefs = self.linear(x, y)
            if self.content.fit_switch == "Power"     : res, coefs = self.power(x, y)
            if self.content.fit_switch == "Exponent"  : res, coefs = self.exponent(x, y)
            if self.content.fit_switch == "Logarithm" : res, coefs = self.logarithm(x, y)
            
            data.update({'fit'  : res})
            data.update({'coefs': coefs})
            
            self.getOutput(0).value = data
            self.getOutput(0).type  = "df"
            return True
        except Exception as e:
            self.setInvalid()
            self.e = e
            self.getOutput(0).value = {"x" : 0.0}
            self.getOutput(0).type = "df"
            return False

    def lstsq(self, x, y):
        z = np.linalg.lstsq(x, y, rcond=None)
        p = z[0] * x
        return np.sum(p, axis=1), z[0]


    def linear(self, x, y):
        z = np.linalg.lstsq(x, y, rcond=None)
        p = z[0] * x
        return np.sum(p, axis=1), z[0]

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