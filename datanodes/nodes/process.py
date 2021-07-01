
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class ProcessGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 100.0

class ProcessContent(NodeContentWidget):
    def initUI(self):
        self.operation = "To Float"
        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.cb.addItem("To Float")
        self.cb.addItem("To Int")
        self.cb.addItem("Drop NAN")
        self.cb.addItem("Drop Inf")
        self.cb.addItem("Clean")

        layout.addWidget(self.cb)
        self.setLayout(layout)
        self.setWindowTitle("Process node")
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


@register_node(OP_MODE_PROCESS)
class ProcessNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_PROCESS
    op_title = "Process"

    def __init__(self, scene, inputs=[1], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = ProcessContent(self)
        self.grNode  = ProcessGraphicsNode(self)
