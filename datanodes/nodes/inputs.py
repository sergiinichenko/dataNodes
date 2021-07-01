
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class ValueInputGraphicsNode(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 120.0
        self.height = 80.0

class ValueInputContent(NodeContentWidget):
    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.edit)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_VALINPUT)
class ValueInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_VALINPUT
    op_title = "Value input"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = ValueInputContent(self)
        self.grNode  = ValueInputGraphicsNode(self)
