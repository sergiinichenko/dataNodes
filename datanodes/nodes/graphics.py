
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GraphicsOutputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300.0
        self.height = 300.0

class GraphicsOutputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # graph area
        self.graph = Figure()
        self.graph.autofmt_xdate()
        self.axis = self.graph.add_subplot(111)
        self.canvas = FigureCanvas(self.graph)
        self.layout.addWidget(self.canvas)


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
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.resize(data['content-widht'], data['content-height'])
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_GRAPHOUTPUT)
class GraphicsOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_GRAPHOUTPUT
    op_title = "Output plot"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = GraphicsOutputContent(self)
        self.grNode  = GraphicsOutputGraphicsNode(self)


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
                pass
            else:
                pass
            return True






