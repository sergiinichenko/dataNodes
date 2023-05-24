
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import re
import copy
from PyQt5.QtWidgets import QComboBox

class ConvertGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 80
        self.setZValue(5)

class ConvertContent(DataContent):

    def initUI(self):
        super().initUI()
        self.setWindowTitle("Convert node")

        self.operation = "to float"

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)


        self.operator = QComboBox()
        self.operator.addItem("to float")
        self.operator.addItem("to string")

        self.operator.setStyleSheet("margin-bottom: 10px; padding-left:10px; height: 25px;")
        self.layout.addWidget(self.operator, 1, 0, 1, 2)
        self.operator.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        self.operation = self.operator.currentText()
        self.changed.emit()

    def serialize(self):
        res = super().serialize()
        res['oper_ind'] = self.operator.currentIndex()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.operator.setCurrentIndex(data['oper_ind'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_CONV_FLOAT)
class ConvertNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_CONV_FLOAT
    op_title = "Convert"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)
        self.state = ""

    def initInnerClasses(self):
        self.content    = ConvertContent(self)
        self.grNode     = ConvertGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def recalculateNode(self):
        self.setDirty()
        self.eval()

    def evalImplementation(self, silent=False):
        input = self.getInput(0)

        if not input:
            self.setDirty()
            self.setInvalid(False)
            self.e = "Does not have an entry Edge"
            return True

        else:
            try:
                self.setDirty(False)
                self.setInvalid(False)
                if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
                self.e       = ""
                self.value   = input.value
                operator     = self.content.operation

                res = {}
                if operator == "to float"   : res = self.tofloat(self.value)
                if operator == "to string"  : res = self.tostring(self.value)

                self.getOutput(0).value = res
                self.getOutput(0).type  = "df"
                return True
            except Exception as e:
                self.setInvalid()
                self.e = e
                self.getOutput(0).value = {"x" : 0.0}
                self.getOutput(0).type = "df"
                return False


    def tofloat(self, value):
        res = {}

        for name in value:
            res[name] = value[name].astype(np.float32)

        return res


    def tostring(self, value, compare, col):
        res = {}

        sel = value[col] != compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res