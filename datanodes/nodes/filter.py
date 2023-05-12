from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import numpy as np
import re
#from math import *
import copy
from PyQt5.QtWidgets import QComboBox, QLineEdit

class FilterGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 150
        self.setZValue(5)

class FilterContent(DataContent):

    def initUI(self):
        super().initUI()
        self.setWindowTitle("Math node")

        self.operation = "="

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)


        self.col = QComboBox()
        self.col.setStyleSheet("margin-bottom: 5px; padding-left:10px; height: 25px;")
        self.layout.addWidget(self.col, 0, 0, 1, 2)
        self.col.currentIndexChanged.connect(self.selectionchange)


        self.cb = QComboBox()
        self.cb.addItem("Equal")
        self.cb.addItem("Not Equal")
        self.cb.addItem("Greater")
        self.cb.addItem("Greater-Equal")
        self.cb.addItem("Less")
        self.cb.addItem("Less-Equal")

        self.cb.setStyleSheet("margin-bottom: 10px; padding-left:10px; height: 25px;")
        self.layout.addWidget(self.cb, 1, 0, 1, 2)
        self.cb.currentIndexChanged.connect(self.selectionchange)


        self.value = QLineEdit("1.0", self)
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet("height: 20px;")
        self.layout.addWidget(self.value, 2, 0, 1, 2)

    def selectionchange(self,i):
        self.operation = self.cb.currentText()
        self.changed.emit()

    def serialize(self):
        res = super().serialize()
        res['sel_ind'] = self.cb.currentIndex()
        res['col_ind'] = self.col.currentIndex()
        items = [self.col.itemText(i) for i in range(self.col.count())]
        res['options'] = items
        res['value']   = self.value.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.cb.setCurrentIndex(data['sel_ind'])
            self.col.addItems(data['options'])
            self.col.setCurrentIndex(data['col_ind'])
            self.value.setText(data['value'])
            self.node.state = str(data['options'])
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_DATA_FILTER)
class FilterNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_FILTER
    op_title = "Filter"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)
        self.state = ""

    def initInnerClasses(self):
        self.content    = FilterContent(self)
        self.grNode     = FilterGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)
        self.content.value.returnPressed.connect(self.recalculateNode)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def recalculateNode(self):
        self.setDirty()
        self.eval()

    def fillTheColumns(self, value):
        if self.state != str(list(value.keys())):
            self.content.blockSignals(True)
            self.content.col.clear()
            self.content.col.addItems(list(value.keys()))
            self.content.blockSignals(False)
            self.state = str(list(value.keys()))

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
                self.e     = ""
                self.value   = input.value
                self.fillTheColumns(self.value)
                compare = float(self.content.value.text())
                col     = self.content.col.currentText()

                res = {}
                if self.content.operation == "Equal"           : res = self.equal(self.value, compare, col)
                if self.content.operation == "Not Equal"       : res = self.notequal(self.value, compare, col)
                if self.content.operation == "Greater"         : res = self.greater(self.value, compare, col)
                if self.content.operation == "Greater-Equal"   : res = self.greaterequal(self.value, self.compare, col)
                if self.content.operation == "Less"            : res = self.less(self.value, compare, col)
                if self.content.operation == "Less-Equal"      : res = self.lessequal(self.value, compare, col)

                self.getOutput(0).value = res
                self.getOutput(0).type  = "df"
                return True
            except Exception as e:
                self.setInvalid()
                self.e = e
                self.getOutput(0).value = {"x" : 0.0}
                self.getOutput(0).type = "df"
                return False


    def equal(self, value, compare, col):
        res = {}

        sel = value[col] == compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res


    def notequal(self, value, compare, col):
        res = {}

        sel = value[col] != compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res


    def greater(self, value, compare, col):
        res = {}

        sel = value[col] > compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res


    def greaterequal(self, value, compare, col):
        res = {}

        sel = value[col] >= compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res


    def less(self, value, compare, col):
        res = {}

        sel = value[col] < compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res


    def lessequal(self, value, compare, col):
        res = {}

        sel = value[col] <= compare
        res = copy.deepcopy(value)

        for name in res:
            res[name] = res[name][sel]

        return res


