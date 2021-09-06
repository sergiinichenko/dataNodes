
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

LINE_STYLES = ['solid',   'dotted', 'dashed','dashdot', 'solid', 'dotted', 'dashed','dashdot', 'solid', 'dotted', 'dashed','dashdot', 'solid', 'dotted', 'dashed','dashdot', 'dotted', 'dashed','dashdot']
COLORS      = ['#D98880', '#AF7AC5', '#85C1E9', '#6C3483', '#196F3D', '#CB4335', '#58D68D', '#2874A6', '#A2D9CE', '#935116', '#DC7633', '#E59866', '#154360', '#16A085', '#7D6608', '#313131']

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



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
        self.axis   = self.graph.add_subplot(111)
        self.canvas = FigureCanvas(self.graph)
        self.layout.addWidget(self.canvas)


class LineStylePicker(QComboBox):
    def __init__(self, node, name, value=None):
        super().__init__()
        self.node = node
        self.name = name
        self.addItem("solid")
        self.addItem("dashed")
        self.addItem("dashdot")
        self.addItem("dotted")
        if value is not None:
            index = self.findText(value, Qt.MatchFixedString)
            self.setCurrentIndex(index)
        self.currentIndexChanged.connect(self.chageStyle)

    def chageStyle(self):
        self.node.properties.linestyle[self.name] = self.currentText()
        self.node.drawPlot()    


class LineSizePicker(QLineEdit):
    def __init__(self, node, name, text):
        super().__init__()
        self.node = node
        self.name = name
        self.setText(str(text))
        self.textChanged.connect(self.chageSize)

    def chageSize(self):
        try:
            self.node.properties.linesize[self.name] = float(self.text())
            self.node.drawPlot()    
        except Exception as e:
            self.node.e = e
            self.node.properties.linesize[self.name] = float(1.0)
    @property
    def value(self):
        return float(self.text())


class GraphicsProperties(NodeProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)
        self.names     = {}
        self.linesize  = {}
        self.linecolor = {}
        self.linestyle = {}
        self.linetype  = {}
        self.c = 0

    def resetWidgets(self):
        self.resetProperties()
        self.names     = {}
        self.linesize  = {}
        self.linecolor = {}
        self.linestyle = {}
        self.linetype  = {}
        self.c = 0

    def cleanProperties(self):
        value = self.node.value
        x_name = list(value.keys())[0]

        for name in value:
            if name != x_name:
                if name not in self.names : 
                    self.names[name]     = name
                    self.linecolor[name] = COLORS[self.c]
                    self.linestyle[name] = "solid"
                    self.linetype[name]  = "line"
                    self.linesize[name]  = 2.0
                    self.c += 1

        for name in reversed(self.names):
            if name not in value : 
                del self.names[name]
                del self.linecolor[name]
                del self.linestyle[name]
                del self.linetype[name]
                del self.linesize[name]



    def fillWidgets(self):
        for name in self.names : 

            label = QLabel(name + " ", self)        
            label.setStyleSheet("margin-top: 10px;")
            label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

            style = LineStylePicker(self.node, name, self.linestyle[name])
            style.setStyleSheet("margin-top: 10px;")

            self.layout.addWidget(label, self.i, 0)
            self.layout.addWidget(style, self.i, 1)
            self.i += 1


            size  = LineSizePicker(self.node, name, self.linesize[name])
            size.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

            color = QWidget(self)
            color.setStyleSheet("background-color:" + self.linecolor[name] + " ;")

            self.layout.addWidget(size, self.i, 0)
            self.layout.addWidget(color, self.i, 1)
            self.i += 1


    def serialize(self):
        res = super().serialize()
        styles  = []
        colors  = []
        types   = []
        names   = []
        sizes   = []

        for name in self.names:
            styles.append(self.linestyle[name])
            colors.append(self.linecolor[name])
            types.append( self.linetype[name])
            sizes.append( self.linesize[name])
            names.append(name)

        res['styles'] = styles
        res['colors'] = colors
        res['types']  = types
        res['sizes']  = sizes
        res['names']  = names
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.resetWidgets()
                for i, name in enumerate(data['names']):
                    self.names[name]     = name
                    self.linecolor[name] = data['colors'][i]
                    self.linestyle[name] = data['styles'][i]
                    self.linetype[name]  = data['types'][i]
                    self.linesize[name]  = data['sizes'][i]
                    self.c += 1
                self.fillWidgets()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_GRAPHOUTPUT)
class GraphicsOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_GRAPHOUTPUT
    op_title = "Plot"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.linecolor = {}
        self.linestyle = {}
        self.linetype  = {}
        self.linesize  = {}
        self.c = 0
        
    def initInnerClasses(self):
        self.content    = GraphicsOutputContent(self)
        self.grNode     = GraphicsOutputGraphicsNode(self)
        self.properties = GraphicsProperties(self)


    def prepareSettings(self):
        self.properties.resetProperties()
        self.properties.cleanProperties()
        self.properties.fillWidgets()

        return True

    def drawPlot(self):
        self.content.axis.clear()
        x_name = list(self.value.keys())[0]
        x_val  = self.value[x_name]
        for i, name in enumerate(self.value):
            if name != x_name:
                self.content.axis.plot(x_val, self.value[name], label=name, 
                                        color=self.properties.linecolor[name], linestyle=self.properties.linestyle[name],
                                        linewidth=self.properties.linesize[name])
        self.content.axis.legend(loc = 1)
        self.content.axis.set_xlabel(x_name)
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        if isinstance(self.value, dict):
            self.drawPlot()
        else:
            pass
        return True
