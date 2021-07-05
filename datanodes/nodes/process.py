
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class SeparateDFGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 200.0

class SeparateDFContent(NodeContentWidget):
    def initUI(self):
        self.operation = "To Float"
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Separate Data")

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
class SeparateDFNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_PROCESS
    op_title = "Separate data"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_CENTER


    def initInnerClasses(self):
        self.content = SeparateDFContent(self)
        self.grNode  = SeparateDFGraphicsNode(self)


    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.content.textOut.clear()
            self.content.textOut.insertPlainText("NaN")
            return False
        else:            
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            self.value = input_node.value
            self.type  = input_node.type
            self.content.textOut.clear()
            if self.type == "df":
                self.content.textOut.insertPlainText(self.value.to_string())
            else:
                self.content.textOut.insertPlainText(str(self.value))
            return True

