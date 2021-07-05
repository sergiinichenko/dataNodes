
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
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res


    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.resize(data['content-widht'], data['content-height'])
        except Exception as e: 
            dumpException(e)
        return True & res


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
        self.output_socket_position = RIGHT_TOP


    def initInnerClasses(self):
        self.content = SeparateDFContent(self)
        self.grNode  = SeparateDFGraphicsNode(self)


    def generateSockets(self, data, names=None):
        self.clearOutputs()        
        outputs = [SOCKET_DATA_TEXT for l in range(data.shape[1])]
        self.createOutputs(outputs, names)
        self.grNode.height = data.shape[1] * self.socket_spacing + 2.0 * self.socket_spacing
        self.grNode.update()

        self.border_radius = 10.0
        self.padding       = 10.0
        self.title_height = 24.0
        self._hpadding     = 5.0
        self._vpadding     = 5.0

        x, y = self.grNode.width - 2.0 * self.grNode.padding, data.shape[1] * self.socket_spacing + 2.0 * self.socket_spacing - self.grNode.title_height - 2.0 * self.grNode.padding
        self.content.resize(x, y)


    def evalImplementation(self):
        input_edge = self.getInput(0)
        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:            
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            self.value = input_edge.value
            self.type  = input_edge.type

            if self.type == "df":
                print(self.value, self.value.columns)
                if len(self.outputs) != self.value.shape[1]:
                    self.generateSockets(self.value, list(self.value.columns))

                for i, socket in zip(range(len(self.outputs)), self.outputs):
                    socket.value = self.value.iloc[:,i]
                    socket.type  = "float"
            else:
                print("FALSE: ", self.value)
            return True

