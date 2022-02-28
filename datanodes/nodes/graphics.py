
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from sklearn.linear_model import LinearRegression
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt

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
        self.axes   = self.graph.add_subplot(111)
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
        self.addItem(" ")
        self.addItem("o")
        self.addItem("x")
        self.addItem("s")

        if value is not None:
            index = self.findText(value, Qt.MatchFixedString)
            self.setCurrentIndex(index)
        self.currentIndexChanged.connect(self.chageStyle)

    def chageStyle(self):
        item = self.currentText()
        if item == "solid" or item == "dashed" or item == "dashdot" or item == "dotted":
            self.node.properties.graphtype[self.name] = 'line'
            self.node.properties.linestyle[self.name] = item
            self.node.drawPlot()    
        else:
            self.node.properties.graphtype[self.name] = 'scatter'
            self.node.properties.linestyle[self.name] = item
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


class ColorPicker(QWidget):
    def __init__(self, node, name, color=None):
        super().__init__()
        self.color = color
        self.node = node
        self.name = name
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:" + self.color + " ;")

    def mouseReleaseEvent(self, event):
        self.color = QColorDialog.getColor()

        if self.color.isValid():
            print(self.color.name())
            self.setStyleSheet("background-color:" + self.color.name() + " ;")

            try:
                self.node.properties.linecolor[self.name] = self.color.name()
                self.node.drawPlot()    
            except Exception as e:
                self.node.e = e


class PlotProperties(NodeProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)
        self.marginTop  = 10
        self.marginRight= 10
        self.marginBottom= 10
        self.marginLeft = 10
        self.labelsize  = 12.0
        self.ticksize   = 10.0
        self.legendsize = 12.0

        label = QLabel("margins ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 1, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")

        self.marginTopW  = QLineEdit(str(self.marginTop), self)
        self.marginTopW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginTopW, 2, 0, 1, 2)

        self.marginRightW  = QLineEdit(str(self.marginRight), self)
        self.marginRightW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginRightW, 3, 1)

        self.marginLeftW  = QLineEdit(str(self.marginLeft), self)
        self.marginLeftW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginLeftW, 3, 0)

        self.marginBottomW  = QLineEdit(str(self.marginBottom), self)
        self.marginBottomW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginBottomW, 4, 0, 1, 2)
        self.marginBottomW.setStyleSheet("margin-bottom: 15px;")


        label = QLabel("Font sizes ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 5, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")

        label = QLabel("lebels  ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.labelsizeW  = QLineEdit(str(self.labelsize), self)
        self.labelsizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 6, 0)
        self.layout.addWidget(self.labelsizeW, 6, 1)

        label = QLabel("ticks   ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ticksizeW  = QLineEdit(str(self.ticksize), self)
        self.ticksizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 7, 0)
        self.layout.addWidget(self.ticksizeW, 7, 1)

        label = QLabel("legends ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.legendsizeW  = QLineEdit(str(self.legendsize), self)
        self.legendsizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 8, 0)
        self.layout.addWidget(self.legendsizeW, 8, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.legendsizeW.setStyleSheet("margin-bottom: 15px;")

        self.marginTopW.returnPressed.connect(self.updateData)
        self.marginRightW.returnPressed.connect(self.updateData)
        self.marginLeftW.returnPressed.connect(self.updateData)
        self.marginBottomW.returnPressed.connect(self.updateData)
        self.labelsizeW.returnPressed.connect(self.updateData)
        self.ticksizeW.returnPressed.connect(self.updateData)
        self.legendsizeW.returnPressed.connect(self.updateData)

    def updateContent(self):
        self.labelsize    = float(self.labelsizeW.text())
        self.ticksize     = float(self.ticksizeW.text())
        self.legendsize   = float(self.legendsizeW.text())
        self.marginTop    = float(self.marginTopW.text())
        self.marginRight  = float(self.marginRightW.text())
        self.marginLeft   = float(self.marginLeftW.text())
        self.marginBottom = float(self.marginBottomW.text())

    def updateData(self):
        self.updateContent()
        self.node.drawPlot()

    def fillWidgets(self):
        self.marginTopW.setText(str(self.marginTop))
        self.marginRightW.setText(str(self.marginRight))
        self.marginLeftW.setText(str(self.marginLeft))
        self.marginBottomW.setText(str(self.marginBottom))
        self.labelsizeW.setText(str(self.labelsize))
        self.ticksizeW.setText(str(self.ticksize))
        self.legendsizeW.setText(str(self.legendsize))

    def serialize(self):
        res = super().serialize()
        res['margintop']   = self.marginTop
        res['marginright'] = self.marginRight
        res['marginleft']  = self.marginLeft
        res['marginbottom']= self.marginBottom
        res['labelsize']   = self.labelsize
        res['ticksize']    = self.ticksize
        res['legendsize']  = self.legendsize

        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                if 'margintop'    in data : self.marginTop    = data['margintop']  
                if 'marginright'  in data : self.marginRight  = data['marginright'] 
                if 'marginleft'   in data : self.marginLeft   = data['marginleft'] 
                if 'marginbottom' in data : self.marginBottom = data['marginbottom'] 
                if 'labelsize'   in data : self.labelsize = data['labelsize']
                if 'ticksize'    in data : self.ticksize  = data['ticksize']
                if 'legendsize'  in data : self.legendsize  = data['legendsize']

                self.fillWidgets()

            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res















class GraphicsProperties(NodeProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)
        self.names     = {}
        self.linesize  = {}
        self.linecolor = {}
        self.linestyle = {}
        self.graphtype = {}
        self.c = 0
        self.xtitle    = ""
        self.xsize     = 12.0
        self.ytitle    = ""
        self.ysize     = 12.0
        self.ticksize  = 10.0
        self.legendsize = 12.0

    def resetWidgets(self):
        self.resetProperties()
        self.names     = {}
        self.linesize  = {}
        self.linecolor = {}
        self.linestyle = {}
        self.graphtype  = {}
        self.c = 0

    def cleanProperties(self):
        for input in self.node.inputs:
            if not input.value : return 

            value  = input.value
            x_name = list(value.keys())[0]

            for name in value:
                if name != x_name:
                    if name not in self.names : 
                        self.names[name]     = name
                        self.linecolor[name] = COLORS[self.c]
                        self.linestyle[name] = "solid"
                        self.graphtype[name] = "line"
                        self.linesize[name]  = 2.0
                        self.c += 1

        for name in reversed(self.names):
            to_remove = True
            for input in self.node.inputs:
                if name in input.value: 
                    to_remove = False

            if to_remove:
                del self.names[name]
                del self.linecolor[name]
                del self.linestyle[name]
                del self.graphtype[name]
                del self.linesize[name]

    def adjustAxes(self):
        self.xtitle = self.xlabelW.text()
        self.xsize  = float(self.xsizeW.text())
        self.ytitle = self.ylabelW.text()
        self.ysize  = float(self.ysizeW.text())
        self.ticksize = float(self.ticksizeW.text())
        self.legendsize = float(self.legendsizeW.text())
        self.node.drawPlot()


    def fillWidgets(self):
        
        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xsizeW  = QLineEdit(str(self.xsize), self)
        self.xsizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.i, 0)
        self.layout.addWidget(self.xsizeW, self.i, 1)
        self.i += 1

        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.xlabelW.setStyleSheet("margin-bottom: 5px;")
        self.layout.addWidget(self.xlabelW, self.i, 0, 1, 2)
        self.i += 1


        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ysizeW  = QLineEdit(str(self.ysize), self)
        self.ysizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.i, 0)
        self.layout.addWidget(self.ysizeW, self.i, 1)
        self.i += 1

        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ylabelW.setStyleSheet("margin-bottom: 15px;")
        self.layout.addWidget(self.ylabelW, self.i, 0, 1, 2)
        self.i += 1


        label = QLabel("tick", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ticksizeW  = QLineEdit(str(self.ticksize), self)
        self.ticksizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.i, 0)
        self.layout.addWidget(self.ticksizeW, self.i, 1)
        self.i += 1

        label = QLabel("legend", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.legendsizeW  = QLineEdit(str(self.legendsize), self)
        self.legendsizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.i, 0)
        self.layout.addWidget(self.legendsizeW, self.i, 1)
        self.i += 1


        self.xlabelW.returnPressed.connect(self.adjustAxes)
        self.ylabelW.returnPressed.connect(self.adjustAxes)
        self.xsizeW.returnPressed.connect(self.adjustAxes)
        self.ysizeW.returnPressed.connect(self.adjustAxes)
        self.ticksizeW.returnPressed.connect(self.adjustAxes)
        self.legendsizeW.returnPressed.connect(self.adjustAxes)

        for name in self.names : 

            label = QLabel(name + " ", self)        
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            style = LineStylePicker(self.node, name, self.linestyle[name])

            label.setStyleSheet("margin-top: 15px;")
            style.setStyleSheet("margin-top: 15px;")

            self.layout.addWidget(label, self.i, 0)
            self.layout.addWidget(style, self.i, 1)
            self.i += 1


            size  = LineSizePicker(self.node, name, self.linesize[name])
            size.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            color = ColorPicker(self.node, name, color=self.linecolor[name])


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
            types.append( self.graphtype[name])
            sizes.append( self.linesize[name])
            names.append(name)

        res['styles'] = styles
        res['colors'] = colors
        res['types']  = types
        res['sizes']  = sizes
        res['names']  = names
        res['xtitle'] = self.xtitle
        res['xsize']  = self.xsize
        res['ytitle'] = self.ytitle
        res['ysize']  = self.ysize
        res['ticksize'] = self.ticksize
        res['legendsize'] = self.legendsize
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
                    self.graphtype[name] = data['types'][i]
                    self.linesize[name]  = data['sizes'][i]
                    if 'xtitle' in data : self.xtitle = data['xtitle']
                    if 'xsize'  in data : self.xsize  = data['xsize']
                    if 'ytitle' in data : self.ytitle = data['ytitle']
                    if 'ysize'  in data : self.ysize  = data['ysize']
                    if 'ticksize'  in data : self.ticksize  = data['ticksize']
                    if 'legendsize'  in data : self.legendsize  = data['legendsize']

                    self.c += 1
                self.fillWidgets()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res



@register_node(OP_MODE_PLOT)
class GraphicsOutputNode(ResizableInputNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT
    op_title = "Plot"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.insockets    = []
        self.linecolor = {}
        self.linestyle = {}
        self.graphtype = {}
        self.linesize  = {}
        self.c = 0
        self.input_socket_position  = LEFT_TOP

    def onInputChange(self, new_edge=None):
        self.content.changed.emit()

    def resize(self):
        pass

    def initInnerClasses(self):
        self.content    = GraphicsOutputContent(self)
        self.grNode     = GraphicsOutputGraphicsNode(self)
        self.properties = GraphicsProperties(self)
        self.content.changed.connect(self.recalculateNode)


    def prepareSettings(self):
        self.properties.resetProperties()
        self.properties.cleanProperties()
        self.properties.fillWidgets()
        return True

    def prepareCanvas(self):
        if not self.hasValue(0) : return

        value = self.getInput(0).value
        self.content.axes.clear()
        x_name = list(value.keys())[0]
        self.x_val  = value[x_name]

        if self.properties.xtitle == "":
            self.content.axes.set_xlabel(x_name)
        else:
            self.content.axes.set_xlabel(self.properties.xtitle)

        self.content.axes.set_ylabel(self.properties.ytitle)
        self.content.axes.xaxis.label.set_size( self.properties.xsize )
        self.content.axes.yaxis.label.set_size( self.properties.ysize )

        self.content.axes.tick_params(labelsize= self.properties.ticksize)
        self.content.axes.tick_params(labelsize= self.properties.ticksize)

    def addData(self, value):
        if not value : return 

        x_name = list(value.keys())[0]
        x_val  = value[x_name]
        type = 'line'

        for i, name in enumerate(value):
            if name != x_name:
                if self.properties.graphtype[name] == 'line':
                    self.content.axes.plot(x_val, value[name], label=name, 
                                            color=self.properties.linecolor[name], linestyle=self.properties.linestyle[name],
                                            linewidth=self.properties.linesize[name])

                if self.properties.graphtype[name] == 'scatter':
                    self.content.axes.scatter(x_val, value[name], label=name, 
                                            color=self.properties.linecolor[name], marker=self.properties.linestyle[name],
                                            s=self.properties.linesize[name]*10)

    def drawPlot(self):
        self.content.axes.clear()
        self.prepareCanvas()
        for input in self.insockets:
            self.addData(input.value)
        self.content.axes.legend(loc = 1, fontsize=self.properties.legendsize)
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        self.insockets = self.getInputs()
        if not self.insockets:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            if len(self.insockets) > 0:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = {}

                self.drawPlot()

                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.getOutput(0).value = 0
                self.getOutput(0).type = "float"
                return False










class TernaryPlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig  = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_axes([0.1, 0.1,  0.75, 0.85])
        self.bar  = self.fig.add_axes([0.9, 0.1,  0.05, 0.85])
        super(TernaryPlotCanvas, self).__init__(self.fig)

class TernaryPlotGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300.0
        self.height = 300.0

class TernaryPlotContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.canvas = TernaryPlotCanvas()
        self.layout.addWidget(self.canvas)


    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.updateSize()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res

class TernaryPlotProperties(PlotProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)

        self.levels     = 10
        self.barfont    = 12
        self.xtitle     = ""
        self.ytitle     = ""
        self.ztitle     = ""

        label = QLabel("levels ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.levelsW  = QLineEdit(str(self.levels), self)
        self.levelsW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 9, 0)
        self.layout.addWidget(self.levelsW, 9, 1)
        label.setStyleSheet("margin-bottom: 5px;")
        self.levelsW.setStyleSheet("margin-bottom: 5px;")

        label = QLabel("bar font size ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.barfontW  = QLineEdit(str(self.barfont), self)
        self.barfontW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 10, 0)
        self.layout.addWidget(self.barfontW, 10, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.barfontW.setStyleSheet("margin-bottom: 15px;")


        label = QLabel("Axis names ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 11, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")

        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 12, 0)
        self.layout.addWidget(self.xlabelW, 12, 1)

        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 13, 0)
        self.layout.addWidget(self.ylabelW, 13, 1)

        label = QLabel("z name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.zlabelW  = QLineEdit(self.ztitle, self)
        self.zlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 14, 0)
        self.layout.addWidget(self.zlabelW, 14, 1)

        label.setStyleSheet("margin-bottom: 15px;")
        self.zlabelW.setStyleSheet("margin-bottom: 15px;")

        self.levelsW.returnPressed.connect(self.updateData)
        self.barfontW.returnPressed.connect(self.updateData)
        self.xlabelW.returnPressed.connect(self.updateData)
        self.ylabelW.returnPressed.connect(self.updateData)
        self.zlabelW.returnPressed.connect(self.updateData)


    def updateContent(self):
        super().updateContent()
        self.levels       = int(self.levelsW.text())
        self.barfont      = float(self.barfontW.text())
        self.xtitle       = self.xlabelW.text()
        self.ytitle       = self.ylabelW.text()
        self.ztitle       = self.zlabelW.text()

    def fillWidgets(self):
        super().fillWidgets()
        self.levelsW.setText(str(self.levels))
        self.xlabelW.setText(self.xtitle)
        self.ylabelW.setText(self.ytitle)
        self.zlabelW.setText(self.ztitle)
        self.barfontW.setText(str(self.barfont))

    def serialize(self):
        res = super().serialize()
        res['barfont']    = self.barfont
        res['levels']     = self.levels
        res['xtitle']     = self.xtitle
        res['ytitle']     = self.ytitle
        res['ztitle']     = self.ztitle

        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                if 'levels'      in data : self.levels  = data['levels']
                if 'xtitle'      in data : self.xtitle  = data['xtitle']
                if 'ytitle'      in data : self.ytitle  = data['ytitle']
                if 'ztitle'      in data : self.ztitle  = data['ztitle']
                if 'barfont'     in data : self.barfont = data['barfont']

                self.fillWidgets()

            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_PLOT_TERNARY)
class TernaryPlotNode(ResizableInputNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT_TERNARY
    op_title = "Ternary Diagram"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.vmax = 1.0
        self.vmin = 0.0
        self.cmap = plt.cm.viridis
        self.insockets = []

    def initInnerClasses(self):
        self.content = TernaryPlotContent(self)
        self.grNode  = TernaryPlotGraphicsNode(self)
        self.properties = TernaryPlotProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def prepareSettings(self):
        return True

    def resize(self):
        pass

    def cAxes(self, ax, x, y, pos='x'):
        xmin = x[0]
        xmax = x[-1]
        ymin = y[0]
        ymax = y[-1]
        ax.plot(x, y, color='black')
        
        xt = xmin
        yt = ymin
        dx = (xmax - xmin) / 10
        dy = (ymax - ymin) / 10
        x2 = ( dx * np.cos(1.5708) - dy * np.sin(1.5708) ) / 5 
        y2 = ( dy * np.cos(1.5708) + dx * np.sin(1.5708) ) / 5 
        for i in range(0, 11):
            ax.plot([xt, xt+x2], [yt, yt+y2], color='black')
            ax.text(xt + 1.75*x2, yt + 1.75*y2, i/10,
                    horizontalalignment='center',
                    verticalalignment='center',
                    color='black', fontsize=self.properties.ticksize)
            xt = xt + dx
            yt = yt + dy
        
        
        
    def mesh(self, num):
        # creating mesh 
        sc = 0.5 * np.sqrt(3) * 1.0
        dx = 1.0 / (num)
        dy = 1.0 / (num)
        size = int((num+1) * ((num+1) + 1) / 2)
        xm = np.zeros(size)
        ym = np.zeros(size)
        index = 0
        for i in range(0, (num+1)):
            for n in range(0, i+1):
                xm[index] = 0.5 - 0.5 * i / num + 1.0 * n / num
                ym[index] = (1.0 - dy * i) * sc
                index = index + 1
        
        return np.array([xm, ym]).transpose()
    

    def drawTernary(self, value):
        self.content.canvas.axes.clear()
        if not value : return
        names = list(value.keys())

        # barycentric coords: (a,b,c)
        self.a = np.array( value[names[0]] )
        self.b = np.array( value[names[1]] )
        self.c = np.array( value[names[2]] )
    
        # values is stored in the last column
        self.v = np.array( value[names[-1]] )
        self.vmin = self.v.min()
        self.vmax = self.v.max()

        # translate the data to cartesian corrds
        self.x = 0.5 * ( 2. * self.b + self.c ) / ( self.a + self.b + self.c )
        self.y = 0.5 * np.sqrt(3) * self.c / (self.a + self.b + self.c)
        ylim   = 0.5 * np.sqrt(3) * 1.0
            
        #add frame
        self.cAxes(self.content.canvas.axes, [0, 0.5], [0, ylim])
        self.cAxes(self.content.canvas.axes, [1, 0],   [0, 0])
        self.cAxes(self.content.canvas.axes, [0.5, 1.0], [ylim, 0])
        
        # plot the contour
        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.v, 
                                                  cmap=self.cmap, 
                                                  vmin=self.vmin, vmax=self.vmax,
                                                  levels=self.properties.levels)
        self.content.canvas.bar.set
        self.content.canvas.bar.set_title(names[-1], fontsize = self.properties.barfont)
        self.content.canvas.bar.tick_params(labelsize = self.properties.barfont)
        plt.colorbar(im, cax=self.content.canvas.bar)
        
        
        #position the axis labels
        self.content.canvas.axes.text(1.05, -0.05,  self.properties.ytitle, fontsize=self.properties.labelsize, ha="left")
        self.content.canvas.axes.text(0.50,  0.92,  self.properties.ztitle, fontsize=self.properties.labelsize, ha="center")
        self.content.canvas.axes.text(-0.05,-0.05,  self.properties.xtitle, fontsize=self.properties.labelsize, ha="right")

    def addScatter(self, value):
        names = list(value.keys())

        # barycentric coords: (a,b,c)
        self.a = np.array( value[names[0]] )
        self.b = np.array( value[names[1]] )
        self.c = np.array( value[names[2]] )
    
        # values is stored in the last column
        self.v = np.array( value[names[-1]] )

        # translate the data to cartesian corrds
        self.x = 0.5 * ( 2. * self.b + self.c ) / ( self.a + self.b + self.c )
        self.y = 0.5 * np.sqrt(3) * self.c / (self.a + self.b + self.c)
        ylim   = 0.5 * np.sqrt(3) * 1.0
                    
        # plot the contour
        self.content.canvas.axes.scatter(self.x, self.y, s=200, c=self.v, 
                                         cmap=self.cmap, vmin=self.vmin, vmax=self.vmax, 
                                         edgecolors='black', linewidths=1.0)

    def drawPlot(self):
        self.drawTernary(self.insockets[0].value)
        if len(self.insockets) > 1:
            for input in self.insockets[1:]:
                if input.value:
                    self.addScatter(input.value)

        self.content.canvas.axes.axes.tick_params(labelsize= self.properties.ticksize)

        sc_w = (1.0 - self.properties.marginRight  * 0.01 - self.properties.marginLeft * 0.01)
        sc_h = (1.0 - self.properties.marginBottom * 0.01 - self.properties.marginTop  * 0.01)

        self.content.canvas.bar.set_position([
                            self.properties.marginLeft * 0.01 + sc_w * 0.95, 
                            self.properties.marginBottom * 0.01 + 0.10, 
                            sc_w * 0.05,
                            sc_h * 0.85])

        self.content.canvas.axes.set_position([
                            self.properties.marginLeft * 0.01, 
                            self.properties.marginBottom * 0.01, 
                            sc_w * 0.9, 
                            sc_h])
                    
        self.content.canvas.axes.set_axis_off()
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        self.insockets = self.getInputs()
        if not self.insockets:
            if DEBUG : print("OUTNODE_TXT: no input edge")
            self.setInvalid()
            if DEBUG : print("OUTNODE_TXT: set invalid")
            self.e = "Does not have and intry Node"
            if DEBUG : print("OUTNODE_TXT: clear the content")
            return False
        else:            
            if DEBUG : print("OUTNODE_TXT: process the input edge data")
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("OUTNODE_TXT: reset Dirty and Invalid")
            self.e = ""
            self.value = self.insockets[0].value
            self.drawPlot()

        return True












class HeatMapCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig  = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_axes([0.1,  0.1, 0.75, 0.85])
        self.bar  = self.fig.add_axes([0.90, 0.1, 0.05, 0.75])

        super(HeatMapCanvas, self).__init__(self.fig)

class HeatMapGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300.0
        self.height = 300.0

class HeatMapContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.canvas = HeatMapCanvas()
        self.layout.addWidget(self.canvas)


    def serialize(self):
        res = super().serialize()
        res['width']  = self.node.grNode.width
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.updateSize()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res

class HeatMapProperties(PlotProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)

        self.levels     = 10
        self.xtitle     = ""
        self.ytitle     = ""

        label = QLabel("levels ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.levelsW  = QLineEdit(str(self.levels), self)
        self.levelsW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 9, 0)
        self.layout.addWidget(self.levelsW, 9, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.levelsW.setStyleSheet("margin-bottom: 15px;")

        label = QLabel("Axis names ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 10, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")

        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 11, 0)
        self.layout.addWidget(self.xlabelW, 11, 1)

        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, 12, 0)
        self.layout.addWidget(self.ylabelW, 12, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.ylabelW.setStyleSheet("margin-bottom: 15px;")

        self.levelsW.returnPressed.connect(self.updateData)
        self.xlabelW.returnPressed.connect(self.updateData)
        self.ylabelW.returnPressed.connect(self.updateData)


    def updateContent(self):
        super().updateContent()
        self.levels       = int(self.levelsW.text())
        self.xtitle       = self.xlabelW.text()
        self.ytitle       = self.ylabelW.text()

    def fillWidgets(self):
        super().fillWidgets()
        self.levelsW.setText(str(self.levels))
        self.xlabelW.setText(self.xtitle)
        self.ylabelW.setText(self.ytitle)

    def serialize(self):
        res = super().serialize()

        res['levels']     = self.levels
        res['xtitle']     = self.xtitle
        res['ytitle']     = self.ytitle

        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                if 'levels'      in data : self.levels = data['levels']
                if 'xtitle'      in data : self.xtitle = data['xtitle']
                if 'ytitle'      in data : self.ytitle = data['ytitle']

                self.fillWidgets()

            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res



@register_node(OP_MODE_PLOT_HEATMAP)
class HeatMapNode(ResizableInputNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT_HEATMAP
    op_title = "Heat Map"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.vmax = 1.0
        self.vmin = 0.0
        self.cmap = plt.cm.viridis
        self.insockets = []

    def initInnerClasses(self):
        self.content = HeatMapContent(self)
        self.grNode  = HeatMapGraphicsNode(self)
        self.properties = HeatMapProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def prepareSettings(self):
        """
        self.properties.resetProperties()
        self.properties.cleanProperties()
        self.properties.fillWidgets()
        """
        return True

    def prepareSettings(self):
        return True

    def resize(self):
        pass

    def addMap(self, value):
        self.content.canvas.axes.clear()
        if not value : return
        names = list(value.keys())

        # barycentric coords: (a,b,c)
        self.x = np.array( value[names[0]] )
        self.y = np.array( value[names[1]] )
    
        # values is stored in the last column
        self.z = np.array( value[names[-1]] )
        self.vmin = self.z.min()
        self.vmax = self.z.max()

        # plot the contour
        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.z, 
                                                  cmap=self.cmap, vmin=self.vmin, vmax=self.vmax,
                                                  levels=self.properties.levels)
        self.content.canvas.bar.set_title(names[-1])
        plt.colorbar(im, cax=self.content.canvas.bar)
        self.content.canvas.axes.set_xlabel(self.properties.xtitle, fontsize=self.properties.labelsize)
        self.content.canvas.axes.set_ylabel(self.properties.ytitle, fontsize=self.properties.labelsize)
        
        self.content.canvas.axes.axes.tick_params(labelsize= self.properties.ticksize)
        self.content.canvas.axes.axes.tick_params(labelsize= self.properties.ticksize)

        sc_w = (1.0 - self.properties.marginRight  * 0.01 - self.properties.marginLeft * 0.01)
        sc_h = (1.0 - self.properties.marginBottom * 0.01 - self.properties.marginTop  * 0.01)

        self.content.canvas.axes.set_position([
                            self.properties.marginLeft * 0.01, 
                            self.properties.marginBottom * 0.01, 
                            sc_w * 0.9, 
                            sc_h])

        self.content.canvas.bar.set_position([
                            self.properties.marginLeft * 0.01 + sc_w * 0.95, 
                            self.properties.marginBottom * 0.01, 
                            sc_w * 0.05,
                            sc_h * 0.90])

        """
        self.axes = self.fig.add_axes([0.1,  0.1, 0.75, 0.85])
        self.bar  = self.fig.add_axes([0.90, 0.1, 0.05, 0.75])

        self.content.canvas.axes.text(1.05, -0.05,  names[1], fontsize=24, ha="left")
        self.content.canvas.axes.text(0.50,  0.92,  names[2], fontsize=24, ha="center")
        self.content.canvas.axes.text(-0.05,-0.05,  names[0], fontsize=24, ha="right")
        """
        

    def drawPlot(self):
        self.insockets = self.getInputs()

        for input in self.insockets:
            if input.value:
                self.addMap(input.value)
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        self.insockets = self.getInputs()
        try:
            if not self.insockets:
                if DEBUG : print("OUTNODE_TXT: no input edge")
                self.setInvalid()
                if DEBUG : print("OUTNODE_TXT: set invalid")
                self.e = "Does not have and intry Node"
                if DEBUG : print("OUTNODE_TXT: clear the content")
                return False
            else:            
                if DEBUG : print("OUTNODE_TXT: process the input edge data")
                self.setDirty(False)
                self.setInvalid(False)
                if DEBUG : print("OUTNODE_TXT: reset Dirty and Invalid")
                self.e = ""
                self.drawPlot()

            return True
        except Exception as e:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = e
            return False
