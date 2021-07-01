
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class MathGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 100.0

class MathContent(NodeContentWidget):
    def initUI(self):
        self.operation = "Add"
        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.cb.addItem("Add")
        self.cb.addItem("Substract")
        self.cb.addItem("Multiply")
        self.cb.addItem("Divide")
        self.cb.addItem("Sqrt")
        self.cb.addItem("Sqr")
        self.cb.addItem("Power")

        layout.addWidget(self.cb)
        self.setLayout(layout)
        self.setWindowTitle("Math node")
        self.cb.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        self.operation = self.cb.currentText()

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
