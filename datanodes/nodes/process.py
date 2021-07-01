
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class ProcessGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 80.0

class ProcessContent(NodeContentWidget):
    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.edit)

@register_node(OP_MODE_VALOUTPUT)
class ProcessNode(DataNode):
    icon     = "icons/valoutput.png"
    op_code  = OP_MODE_PROCESS
    op_title = "Process"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = ProcessContent(self)
        self.grNode  = ProcessGraphicsNode(self)
