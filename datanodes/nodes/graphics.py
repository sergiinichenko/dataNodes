
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QComboBox, QWidget, QLineEdit, QColorDialog, QLabel, QGroupBox, QCheckBox
from datanodes.math.convex import ConvexHull2D
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from matplotlib.collections import PathCollection

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
        self.width  = 300
        self.height = 300

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
        self.items  = {}
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
        self.addItem("convex")
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
            self.node.changeStyle(self.name)
            return
        if item == "convex":
            self.node.properties.graphtype[self.name] = 'convex'
            self.node.properties.linestyle[self.name] = item
            self.node.changeStyle(self.name)
            return
        
        self.node.properties.graphtype[self.name] = 'scatter'
        self.node.properties.linestyle[self.name] = item
        self.node.changeStyle(self.name)

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
            self.node.updateStyle(self.name)
        except Exception as e:
            self.node.e = e
            self.node.properties.linesize[self.name] = float(1.0)
            self.node.updateStyle(self.name)
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
            self.setStyleSheet("background-color:" + self.color.name() + " ;")

            try:
                self.node.properties.maincolor[self.name] = self.color.name()
                self.node.updateStyle(self.name)
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
        self.xtitle    = ""
        self.ytitle    = ""
        self.x_limit_min = 0.0
        self.x_limit_max = 1.0
        self.y_limit_min = 0.0
        self.y_limit_max = 1.0
        self.grid_main = False
        self.grid_minor = False
        self.pos        = 1


        label = QLabel("margins ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1
        
        self.marginTopW  = QLineEdit(str(self.marginTop), self)
        self.marginTopW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginTopW, 2, 0, 1, 2)
        self.pos+=1

        self.marginRightW  = QLineEdit(str(self.marginRight), self)
        self.marginRightW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginRightW, self.pos, 1)

        self.marginLeftW  = QLineEdit(str(self.marginLeft), self)
        self.marginLeftW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginLeftW, self.pos, 0)
        self.pos+=1

        self.marginBottomW  = QLineEdit(str(self.marginBottom), self)
        self.marginBottomW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.marginBottomW, self.pos, 0, 1, 2)
        self.marginBottomW.setStyleSheet("margin-bottom: 15px;")
        self.pos+=1


        label = QLabel("Font sizes ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1

        label = QLabel("lebels  ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.labelsizeW  = QLineEdit(str(self.labelsize), self)
        self.labelsizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.labelsizeW, self.pos, 1)
        self.pos+=1

        label = QLabel("ticks   ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ticksizeW  = QLineEdit(str(self.ticksize), self)
        self.ticksizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.ticksizeW, self.pos, 1)
        self.pos+=1

        label = QLabel("legends ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.legendsizeW  = QLineEdit(str(self.legendsize), self)
        self.legendsizeW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.legendsizeW, self.pos, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.legendsizeW.setStyleSheet("margin-bottom: 15px;")
        self.pos+=1

        label = QLabel("Axis names ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1

        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.xlabelW, self.pos, 1)
        self.pos+=1

        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.ylabelW, self.pos, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.ylabelW.setStyleSheet("margin-bottom: 15px;")
        self.pos+=1

        self.limits_grid = QGridLayout()
        self.limits      = QGroupBox()
        self.limits.setLayout(self.limits_grid)
        self.layout.addWidget(self.limits, self.pos, 0, 3, 2)
        self.pos+=1
        

        label = QLabel("Axis limits ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(label, 0, 0, 1, 2)

        label = QLabel("x", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(label, 1, 0)

        self.x_limit_minW  = QLineEdit(str(self.x_limit_min), self)
        self.x_limit_minW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(self.x_limit_minW, 1, 1)

        self.x_limit_maxW  = QLineEdit(str(self.x_limit_max), self)
        self.x_limit_maxW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(self.x_limit_maxW, 1, 2)


        label = QLabel("y", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(label, 2, 0)

        self.y_limit_minW  = QLineEdit(str(self.y_limit_min), self)
        self.y_limit_minW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(self.y_limit_minW, 2, 1)

        self.y_limit_maxW  = QLineEdit(str(self.y_limit_max), self)
        self.y_limit_maxW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.limits_grid.addWidget(self.y_limit_maxW, 2, 2)


        self.limits_reset = QPushButton("Reset")
        self.limits_reset.clicked.connect(self.resetLimits)
        self.limits_grid.addWidget(self.limits_reset, 3, 0, 1, 3)
        self.limits.setStyleSheet("margin-bottom: 15px;")


        # Part related to Grid settings
        # General container

        label = QLabel("Main grid", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet("margin-right: 10px;")
        self.layout.addWidget(label, self.pos, 0)

        self.main_grid_swith = QCheckBox("Grid main")
        self.main_grid_swith.setChecked(False)
        self.layout.addWidget(self.main_grid_swith, self.pos, 1)
        self.pos+=1


        label = QLabel("Minor grid", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet("margin-right: 10px;")
        self.layout.addWidget(label, self.pos, 0)

        self.minor_grid_swith = QCheckBox("Grid minor")
        self.minor_grid_swith.setChecked(False)
        self.layout.addWidget(self.minor_grid_swith, self.pos, 1)
        self.pos+=1


        # Return Pressed event listeners
        self.marginTopW.returnPressed.connect(self.updateData)
        self.marginRightW.returnPressed.connect(self.updateData)
        self.marginLeftW.returnPressed.connect(self.updateData)
        self.marginBottomW.returnPressed.connect(self.updateData)
        self.labelsizeW.returnPressed.connect(self.updateData)
        self.ticksizeW.returnPressed.connect(self.updateData)
        self.legendsizeW.returnPressed.connect(self.updateData)
        self.xlabelW.returnPressed.connect(self.updateData)
        self.ylabelW.returnPressed.connect(self.updateData)
        self.x_limit_minW.returnPressed.connect(self.updateData)
        self.x_limit_maxW.returnPressed.connect(self.updateData)
        self.y_limit_minW.returnPressed.connect(self.updateData)
        self.y_limit_maxW.returnPressed.connect(self.updateData)
        self.main_grid_swith.stateChanged.connect(self.updateData)
        self.minor_grid_swith.stateChanged.connect(self.updateData)


    def updateContent(self):
        self.labelsize      = float(self.labelsizeW.text())
        self.ticksize       = float(self.ticksizeW.text())
        self.legendsize     = float(self.legendsizeW.text())
        self.marginTop      = float(self.marginTopW.text())
        self.marginRight    = float(self.marginRightW.text())
        self.marginLeft     = float(self.marginLeftW.text())
        self.marginBottom   = float(self.marginBottomW.text())
        self.xtitle         = self.xlabelW.text()
        self.ytitle         = self.ylabelW.text()
        self.x_limit_min    = float(self.x_limit_minW.text())
        self.x_limit_max    = float(self.x_limit_maxW.text())
        self.y_limit_min    = float(self.y_limit_minW.text())
        self.y_limit_max    = float(self.y_limit_maxW.text())
        self.grid_main      = self.main_grid_swith.isChecked()
        self.grid_minor     = self.minor_grid_swith.isChecked()

    def updateData(self):
        self.updateContent()
        self.node.drawPlot()

    def resetLimits(self):
        xmin, xmax, ymin, ymax = self.node.getDataLimits()
        self.x_limit_minW.setText(str(xmin))
        self.x_limit_maxW.setText(str(xmax))
        self.y_limit_minW.setText(str(ymin))
        self.y_limit_maxW.setText(str(ymax))
        self.updateData()


    def fillWidgets(self):
        self.marginTopW.setText(str(self.marginTop))
        self.marginRightW.setText(str(self.marginRight))
        self.marginLeftW.setText(str(self.marginLeft))
        self.marginBottomW.setText(str(self.marginBottom))
        self.labelsizeW.setText(str(self.labelsize))
        self.ticksizeW.setText(str(self.ticksize))
        self.legendsizeW.setText(str(self.legendsize))
        self.xlabelW.setText(self.xtitle)
        self.ylabelW.setText(self.ytitle)
        self.x_limit_minW.setText(str(self.x_limit_min))
        self.x_limit_maxW.setText(str(self.x_limit_max))
        self.y_limit_minW.setText(str(self.y_limit_min))
        self.y_limit_maxW.setText(str(self.y_limit_max))
        self.appendDataWidgets()
        
    def appendDataWidgets(self):
        pass
        
    def serialize(self):
        res = super().serialize()
        res['margintop']    = self.marginTop
        res['marginright']  = self.marginRight
        res['marginleft']   = self.marginLeft
        res['marginbottom'] = self.marginBottom
        res['labelsize']    = self.labelsize
        res['ticksize']     = self.ticksize
        res['legendsize']   = self.legendsize
        res['xtitle']       = self.xtitle
        res['ytitle']       = self.ytitle
        res['x_limit_min']  = self.x_limit_min
        res['x_limit_max']  = self.x_limit_max
        res['y_limit_min']  = self.y_limit_min
        res['y_limit_max']  = self.y_limit_max
        res['grid_main']    = self.grid_main
        res['grid_minor']   = self.grid_minor
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                if 'margintop'    in data : self.marginTop    = data['margintop']  
                if 'marginright'  in data : self.marginRight  = data['marginright'] 
                if 'marginleft'   in data : self.marginLeft   = data['marginleft'] 
                if 'marginbottom' in data : self.marginBottom = data['marginbottom'] 
                if 'labelsize'    in data : self.labelsize    = data['labelsize']
                if 'ticksize'     in data : self.ticksize     = data['ticksize']
                if 'legendsize'   in data : self.legendsize   = data['legendsize']
                if 'xtitle'       in data : self.xtitle       = data['xtitle']
                if 'ytitle'       in data : self.ytitle       = data['ytitle']
                if 'x_limit_min'  in data : self.x_limit_min  = data['x_limit_min']
                if 'x_limit_max'  in data : self.x_limit_max  = data['x_limit_max']
                if 'y_limit_min'  in data : self.y_limit_min  = data['y_limit_min']
                if 'y_limit_max'  in data : self.y_limit_max  = data['y_limit_max']
                if 'grid_main'    in data : self.grid_main    = data['grid_main'] 
                if 'grid_minor'   in data : self.grid_minor   = data['grid_minor']

                self.main_grid_swith.setChecked(self.grid_main)
                self.minor_grid_swith.setChecked(self.grid_minor)

                self.fillWidgets()

            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res















class GraphicsProperties(PlotProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)
        self.names     = {}
        self.linesize  = {}
        self.maincolor = {}
        self.linestyle = {}
        self.graphtype = {}
        self.c = 0

        self.labels    = {}
        self.styles    = {}
        self.sizes     = {}
        self.colors    = {}

    def appendDataWidgets(self):
        for name in self.names : 
            self.appendDataWidget(name)
            
    def appendDataWidget(self, name):
        if name in self.names : return
        self.names[name]      = name
        self.maincolor[name]  = COLORS[np.random.randint(0, len(COLORS))]
        self.linestyle[name]  = "solid"
        self.graphtype[name]  = "line"
        self.linesize[name]   = 2.0

        self.labels[name] = QLabel(name + " ", self)        
        self.labels[name].setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.styles[name] = LineStylePicker(self.node, name, self.linestyle[name])

        self.labels[name].setStyleSheet("margin-top: 15px;")
        self.styles[name].setStyleSheet("margin-top: 15px;")

        self.layout.addWidget(self.labels[name], self.pos, 0)
        self.layout.addWidget(self.styles[name], self.pos, 1)
        self.pos += 1


        self.sizes[name]  = LineSizePicker(self.node, name, self.linesize[name])
        self.sizes[name].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.colors[name] = ColorPicker(self.node, name, color=self.maincolor[name])


        self.layout.addWidget(self.sizes[name],  self.pos, 0)
        self.layout.addWidget(self.colors[name], self.pos, 1)
        self.pos += 1
        
        
    def removeWidget(self, name):
        if name in self.labels:
            self.layout.removeWidget(self.labels[name])
            self.layout.removeWidget(self.styles[name])
            self.layout.removeWidget(self.sizes[name])
            self.layout.removeWidget(self.colors[name])

            self.labels[name].setParent(None)
            self.styles[name].setParent(None)
            self.sizes[name].setParent(None)
            self.colors[name].setParent(None)
            
            del self.labels[name]
            del self.styles[name]
            del self.sizes[name]
            del self.colors[name]

            del self.names[name]
            del self.maincolor[name]
            del self.linestyle[name]
            del self.graphtype[name]
            del self.linesize[name]

            self.pos -= 1

    def setupWidget(self, name):
        index = self.styles[name].findText(self.linestyle[name], Qt.MatchFixedString)
        self.styles[name].currentIndexChanged.disconnect()
        self.styles[name].setCurrentIndex(index)
        self.styles[name].currentIndexChanged.connect(self.styles[name].chageStyle)
        #self.styles[name].chageStyle()

        self.sizes[name].setText(str(self.linesize[name]))
        #self.sizes[name].chageSize()

        self.colors[name].setStyleSheet("background-color:" + self.maincolor[name] + " ;")
        #self.node.drawPlot()    


    def serialize(self):
        res = super().serialize()
        res["colors"] = {}
        res["styles"] = {}
        res["widths"] = {}
        res["grapth"] = {}
        for name in self.names:
            if name not in self.maincolor : self.maincolor[name] = COLORS[np.random.randint(0, 10)]
            if name not in self.linestyle : self.linestyle[name] = "solid"
            if name not in self.linesize  : self.linesize [name] = 2
            if name not in self.graphtype : self.graphtype[name] = "line"
            res["names"] = self.names
            res["colors"][name] = self.maincolor[name]
            res["styles"][name] = self.linestyle[name]
            res["widths"][name] = self.linesize[name]
            res["grapth"][name] = self.graphtype[name]
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                for name in data["names"]:
                    self.appendDataWidget(name)
                    if 'colors' in data: 
                        if name in data["colors"] : self.maincolor[name] = data['colors'][name]
                    if 'styles' in data: 
                        if name in data["styles"] : self.linestyle[name] = data['styles'][name]
                    if 'widths' in data: 
                        if name in data["widths"] : self.linesize[name]  = data['widths'][name]
                    if 'grapth' in data: 
                        if name in data["grapth"] : self.graphtype[name] = data['grapth'][name]
                    self.setupWidget(name)
                return True                
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
        self.maincolor = {}
        self.linestyle = {}
        self.graphtype = {}
        self.linesize  = {}
        self.all_names = []
        self.c = 0
        self.input_socket_position  = LEFT_TOP
        self.convex  = ConvexHull2D()

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
        #self.properties.resetProperties()
        #self.properties.cleanProperties()
        #self.properties.fillWidgets()
        return True

    def prepareCanvas(self):
        self.all_names = []
        if not self.hasValue(0) : return

        value = self.getInput(0).value

        x_name = list(value.keys())[0]
        self.x_val  = value[x_name]

        if self.properties.xtitle == "":
            self.content.axes.set_xlabel(x_name)
        else:
            self.content.axes.set_xlabel(self.properties.xtitle)

        if self.properties.grid_main:
            self.content.axes.grid(visible=True, which="major")
        else:
            self.content.axes.grid(visible=False, which="major")

        if self.properties.grid_minor:
            self.content.axes.grid(visible=True, which="minor")
        else:
            self.content.axes.grid(visible=False, which="minor")

        self.content.axes.set_ylabel(self.properties.ytitle)
        self.content.axes.xaxis.label.set_size( self.properties.labelsize )
        self.content.axes.yaxis.label.set_size( self.properties.labelsize )

        self.content.axes.tick_params(labelsize= self.properties.ticksize)
        self.content.axes.tick_params(labelsize= self.properties.ticksize)

        self.content.axes.set_xlim(self.properties.x_limit_min, self.properties.x_limit_max)
        self.content.axes.set_ylim(self.properties.y_limit_min, self.properties.y_limit_max)


    def addData(self, value):
        # if no input then return
        if not value : return 

        x_name = list(value.keys())[0]
        x_val  = value[x_name]

        # update the input
        for name in value:
            if name != x_name:
                # name is not in the properties 
                if name not in self.content.items : continue
                if name not in self.all_names : self.all_names.extend([name])
                #define the min length of the data to avoin error caused by size difference
                ln = min(len(x_val), len(value[name]))

                self.updateData(name, x_val[0:ln], value[name][0:ln])
                self.updateStyle(name)
        
        # add what is missing
        for name in value:
            if name != x_name:
                # name is in the properties and has been already updated
                if name in self.content.items : continue
                if name not in self.all_names : self.all_names.extend([name])

                self.properties.appendDataWidget(name)
                #define the min length of the data to avoin error caused by size difference
                ln = min(len(x_val), len(value[name]))

                if self.properties.graphtype[name] == 'line':
                    self.content.items[name], = self.content.axes.plot(x_val[0:ln], value[name][0:ln], label=name, 
                                            color=self.properties.maincolor[name], linestyle=self.properties.linestyle[name],
                                            linewidth=self.properties.linesize[name])

                if self.properties.graphtype[name] == 'scatter':
                    self.content.items[name] = self.content.axes.scatter(x_val[0:ln], value[name][0:ln], label=name, 
                                            color=self.properties.maincolor[name], marker=self.properties.linestyle[name],
                                            s=self.properties.linesize[name]*10)

                if self.properties.graphtype[name] == 'convex':
                    # barycentric coords: (a,b,c)
                    data   = np.column_stack([x_val[0:ln], value[name][0:ln]])
                    data   = data[np.logical_not(np.isnan(data).any(axis=1)),:]
                    try:
                        points = self.convex(data)
                    except Exception as e:
                        points = data
                    #By adding the head to the tail, we close the polygon during plotting
                    points = np.vstack([points, points[0]])

                    xi = points[:,0]
                    yi = points[:,1]

                    self.content.items[name], = self.content.axes.fill(xi, yi, color=self.properties.maincolor[name], label=name)

        # remove what is not in the values
        for name in list(self.content.items.keys()):
            # name is in the plot input and does not have to be removed
            if name in self.all_names : continue
            
            if isinstance(self.content.items[name], Line2D):
                self.content.axes.lines.remove(self.content.items[name])
            if isinstance(self.content.items[name], Polygon):
                self.content.axes.patches.remove(self.content.items[name])
            if isinstance(self.content.items[name], PathCollection):
                self.content.axes.collections.remove(self.content.items[name])            

            del self.content.items[name]
            self.properties.removeWidget(name)
            self.content.canvas.draw()
            
    def updateData(self, name, x, y):
        if isinstance(self.content.items[name], Line2D):
            self.content.items[name].set_xdata(x)
            self.content.items[name].set_ydata(y)

        if isinstance(self.content.items[name], PathCollection):
            data   = np.column_stack([x, y])
            self.content.items[name].set_offsets(data)

        if isinstance(self.content.items[name], Polygon):
            # barycentric coords: (a,b,c)
            data   = np.column_stack([x, y])
            data   = data[np.logical_not(np.isnan(data).any(axis=1)),:]
            points = self.convex(data)
            #By adding the head to the tail, we close the polygon during plotting
            points = np.vstack([points, points[0]])
            self.content.items[name].set_xy(points)
        

    def updateStyle(self, name):
        if name not in self.content.items : return

        if isinstance(self.content.items[name], Line2D):
            self.content.items[name].set(label=name, color=self.properties.maincolor[name])
            self.content.items[name].set(linestyle=self.properties.linestyle[name],
                                            linewidth=self.properties.linesize[name])
        if isinstance(self.content.items[name], PathCollection):
            xy = self.content.items[name].get_offsets()
            x = xy[:,0]
            y = xy[:,1]
            self.content.axes.collections.remove(self.content.items[name])
            del self.content.items[name]
            self.content.items[name] = self.content.axes.scatter(x, y, label=name, 
                                    color=self.properties.maincolor[name], marker=self.properties.linestyle[name],
                                    s=self.properties.linesize[name]*10)

        if isinstance(self.content.items[name], Polygon):
            self.content.items[name].set(label=name, color=self.properties.maincolor[name])

        self.content.canvas.draw()

        
    def changeStyle(self, name):
        if name not in self.content.items : return

        x, y = [], []
        if isinstance(self.content.items[name], Line2D):
            x = self.content.items[name].get_xdata()
            y = self.content.items[name].get_ydata()
            self.content.axes.lines.remove(self.content.items[name])
        if isinstance(self.content.items[name], Polygon):
            xy = self.content.items[name].get_xy()
            x = xy[:,0]
            y = xy[:,1]
            self.content.axes.patches.remove(self.content.items[name])
        if isinstance(self.content.items[name], PathCollection):
            xy = self.content.items[name].get_offsets()
            x = xy[:,0]
            y = xy[:,1]
            self.content.axes.collections.remove(self.content.items[name])
        
        del self.content.items[name]
                
        if self.properties.graphtype[name] == 'line':
            self.content.items[name], = self.content.axes.plot(x, y, label=name, 
                                    color=self.properties.maincolor[name], linestyle=self.properties.linestyle[name],
                                    linewidth=self.properties.linesize[name])

        if self.properties.graphtype[name] == 'scatter':
            self.content.items[name] = self.content.axes.scatter(x, y, label=name, 
                                    color=self.properties.maincolor[name], marker=self.properties.linestyle[name],
                                    s=self.properties.linesize[name]*10)

        if self.properties.graphtype[name] == 'convex':
            data   = np.column_stack([x, y])
            data   = data[np.logical_not(np.isnan(data).any(axis=1)),:]
            points = self.convex(data)
            #By adding the head to the tail, we close the polygon during plotting
            points = np.vstack([points, points[0]])

            xi = points[:,0]
            yi = points[:,1]
            self.content.items[name], = self.content.axes.fill(xi, yi, c=self.properties.maincolor[name], label=name)

        self.content.canvas.draw()
            
            
    def drawPlot(self):
        try:
            #self.content.axes.clear()
            self.prepareCanvas()
            for input in self.insockets:
                self.addData(input.value)
            self.content.axes.legend(loc = 1, fontsize=self.properties.legendsize)
            self.content.canvas.draw()
        except Exception as e:
            print(e)


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
        self.width  = 300
        self.height = 300

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
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.levelsW, self.pos, 1)
        label.setStyleSheet("margin-bottom: 5px;")
        self.levelsW.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1

        label = QLabel("bar font size ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.barfontW  = QLineEdit(str(self.barfont), self)
        self.barfontW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.barfontW, self.pos, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.barfontW.setStyleSheet("margin-bottom: 15px;")
        self.pos+=1


        label = QLabel("Axis names ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1

        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.xlabelW, self.pos, 1)
        self.pos+=1

        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.ylabelW, self.pos, 1)
        self.pos+=1

        label = QLabel("z name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.zlabelW  = QLineEdit(self.ztitle, self)
        self.zlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.zlabelW, self.pos, 1)
        self.pos+=1

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

        try : 
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
        except Exception as e : dumpException(e)

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
        self.width  = 300
        self.height = 300

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
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.levelsW, self.pos, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.levelsW.setStyleSheet("margin-bottom: 15px;")
        self.pos+=1

        label = QLabel("Axis names ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1

        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.xlabelW, self.pos, 1)
        self.pos+=1

        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.ylabelW, self.pos, 1)
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
    
    def interpolate(self, x, y, z, xi, yi):
        return z

    def addMap(self, value):
        ngridx = 50
        ngridy = 50
        self.content.canvas.axes.clear()
        if not value : return
        names = list(value.keys())

        # barycentric coords: (a,b,c)
        self.x = value[names[0]] # np.unique( )
        self.y = value[names[1]] # np.unique( )
    
        # values is stored in the last column
        self.z = np.array( value[names[-1]] )
        self.vmin = self.z.min()
        self.vmax = self.z.max()

        # plot the contour
        """
        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.z, 
                                                  cmap=self.cmap, vmin=self.vmin, vmax=self.vmax,
                                                  levels=self.properties.levels)
        """

        # Create grid values first.
        xi = np.linspace(np.min(self.x), np.max(self.x), ngridx)
        yi = np.linspace(np.min(self.y), np.max(self.y), ngridy)

        # Linearly interpolate the data (x, y) on a grid defined by (xi, yi).
        #zi = griddata((self.x, self.y), self.z, (xi[None,:], yi[:,None]), method='linear')

        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.z, levels=self.properties.levels, 
                                               cmap=self.cmap, vmin=self.vmin, vmax=self.vmax)

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











class ContourCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig  = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_axes([0.1,  0.1, 0.75, 0.85])

        super(ContourCanvas, self).__init__(self.fig)

class ContourGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300
        self.height = 300

class ContourContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.canvas = ContourCanvas()
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

class ContourProperties(PlotProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)

        self.levels     = 10
        self.xtitle     = ""
        self.ytitle     = ""

        label = QLabel("levels ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.levelsW  = QLineEdit(str(self.levels), self)
        self.levelsW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.levelsW, self.pos, 1)
        label.setStyleSheet("margin-bottom: 15px;")
        self.levelsW.setStyleSheet("margin-bottom: 15px;")
        self.pos+=1

        label = QLabel("Axis names ", self)        
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0, 1, 2)
        label.setStyleSheet("margin-bottom: 5px;")
        self.pos+=1

        label = QLabel("x name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xlabelW  = QLineEdit(self.xtitle, self)
        self.xlabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.xlabelW, self.pos, 1)
        self.pos+=1

        label = QLabel("y name ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ylabelW  = QLineEdit(self.ytitle, self)
        self.ylabelW.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(label, self.pos, 0)
        self.layout.addWidget(self.ylabelW, self.pos, 1)
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



@register_node(OP_MODE_PLOT_CONTOUR)
class ContourNode(ResizableInputNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT_CONTOUR
    op_title = "Contour"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.vmax = 1.0
        self.vmin = 0.0
        self.cmap = plt.cm.viridis
        self.insockets = []

    def initInnerClasses(self):
        self.content    = ContourContent(self)
        self.grNode     = ContourGraphicsNode(self)
        self.properties = ContourProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def prepareSettings(self):
        return True

    def prepareSettings(self):
        return True

    def resize(self):
        pass
    
    def interpolate(self, x, y, z, xi, yi):
        return z

    def addMap(self, value, name, val):
        ngridx = 50
        ngridy = 50
        self.content.canvas.axes.clear()
        if not value : return
        names = list(value.keys())

        # barycentric coords: (a,b,c)
        self.x = value[names[0]] # np.unique( )
        self.y = value[name] # np.unique( )
    
        # values is stored in the last column
        self.z = np.ones(len(value[name])) * val
        self.vmin = 0.0
        self.vmax = val

        # plot the contour
        """
        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.z, 
                                                  cmap=self.cmap, vmin=self.vmin, vmax=self.vmax,
                                                  levels=self.properties.levels)
        """

        # Create grid values first.
        xi = np.linspace(np.min(self.x), np.max(self.x), ngridx)
        yi = np.linspace(np.min(self.y), np.max(self.y), ngridy)

        # Linearly interpolate the data (x, y) on a grid defined by (xi, yi).
        #zi = griddata((self.x, self.y), self.z, (xi[None,:], yi[:,None]), method='linear')

        #im = self.content.canvas.axes.contourf(self.x, self.y, self.z, levels=self.properties.levels, 
        #                                       cmap=self.cmap, vmin=self.vmin, vmax=self.vmax)
        im = self.content.canvas.axes.tricontourf(self.x, self.y, self.z, levels=self.properties.levels, 
                                       cmap=self.cmap, vmin=self.vmin, vmax=self.vmax)

    def prepareCanvas(self):
        if not self.hasValue(0) : return

        value = self.getInput(0).value
        self.content.canvas.axes.clear()
        x_name = list(value.keys())[0]
        self.x_val  = value[x_name]

        if self.properties.xtitle == "":
            self.content.canvas.axes.set_xlabel(x_name)
        else:
            self.content.canvas.axes.set_xlabel(self.properties.xtitle)

        #if self.properties.grid_main:
        #    self.content.canvas.axes.grid(visible=True, which="major")
        #else:
        #    self.content.canvas.axes.grid(visible=False, which="major")

        #if self.properties.grid_minor:
        #    self.content.canvas.axes.grid(visible=True, which="minor")
        #else:
        #    self.content.canvas.axes.grid(visible=False, which="minor")

        #self.content.canvas.axes.set_ylabel(self.properties.ytitle)
        #self.content.canvas.axes.xaxis.label.set_size( self.properties.labelsize )
        #self.content.canvas.axes.yaxis.label.set_size( self.properties.labelsize )

        self.content.canvas.axes.tick_params(labelsize= self.properties.ticksize)
        self.content.canvas.axes.tick_params(labelsize= self.properties.ticksize)

        #self.content.canvas.axes.set_xlim(self.properties.x_limit_min, self.properties.x_limit_max)
        #self.content.canvas.axes.set_ylim(self.properties.y_limit_min, self.properties.y_limit_max)
        

    def drawPlot(self):
        self.insockets = self.getInputs()

        self.content.canvas.axes.clear()
        self.prepareCanvas()

        for input in self.insockets:
            if input.value:
                self.value = input.value
                count = 1.0
                for name in list(self.value.keys())[1:]:
                    self.addMap(self.value, name, count)
                    count += 1.0
                    
        self.content.canvas.axes.legend(loc = 1, fontsize=self.properties.legendsize)
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

















class HistogramProperties(PlotProperties):
    def __init__(self, node, parent=None):
        super().__init__(node)
        self.names     = {}
        self.maincolor = {}
        self.alphas    = {}
        self.bins      = QLineEdit("20", self)
        self.c = 0

        self.labels    = {}
        self.colors    = {}

    def appendDataWidgets(self):
        self.bins  = QLineEdit(20, self)
        self.bins_label = QLabel("bins ", self)
        self.bins_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.layout.addWidget(self.bins_label, self.pos, 0)
        self.layout.addWidget(self.bins, self.pos, 1)
        self.pos += 1

        for name in self.names : 
            self.appendDataWidget(name)
            
    def appendDataWidget(self, name):
        if name in self.names : return
        self.names[name]      = name
        self.maincolor[name]  = COLORS[np.random.randint(0, len(COLORS))]

        self.labels[name] = QLabel(name + " ", self)
        self.labels[name].setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.labels[name].setStyleSheet("margin-top: 15px;")

        self.layout.addWidget(self.labels[name], self.pos, 0)
        self.pos += 1


        self.alphas[name]  = QLineEdit("0.5", self)
        self.alphas[name].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.colors[name] = ColorPicker(self.node, name, color=self.maincolor[name])

        self.layout.addWidget(self.alphas[name], self.pos, 0)
        self.layout.addWidget(self.colors[name], self.pos, 1)
        self.pos += 1
        
        
    def removeWidget(self, name):
        if name in self.labels:
            self.layout.removeWidget(self.labels[name])
            self.layout.removeWidget(self.sizes[name])
            self.layout.removeWidget(self.colors[name])

            self.labels[name].setParent(None)
            self.colors[name].setParent(None)
            
            del self.labels[name]
            del self.colors[name]

            del self.names[name]
            del self.maincolor[name]
            del self.alphas[name]

            self.pos -= 1

    def setupWidget(self, name):
        index = self.colors[name].findText(self.linestyle[name], Qt.MatchFixedString)

        self.alphas[name].setText(str(self.alphas[name]))

        self.colors[name].setStyleSheet("background-color:" + self.maincolor[name] + " ;")


    def serialize(self):
        res = super().serialize()
        res["colors"] = {}
        res["alphas"] = {}
        res["bins"] = self.bins.text()
        for name in self.names:
            if name not in self.maincolor : self.maincolor[name] = COLORS[np.random.randint(0, 10)]
            if name not in self.alphas    : self.alphas[name]   = 0.5
            res["names"] = self.names
            res["colors"][name] = self.maincolor[name]
            res["alphas"][name] = self.alphas[name]
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                if 'bins' in data : self.bins = data['bins']
                for name in data["names"]:
                    self.appendDataWidget(name)
                    if 'colors' in data: 
                        if name in data["colors"] : self.maincolor[name] = data['colors'][name]
                    if 'alpha' in data: 
                        if name in data["alpha"] : self.alpha[name]      = data['alpha'][name]
                    self.setupWidget(name)
                return True                
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res



@register_node(OP_MODE_PLOT_HISTOGRAM)
class HistogramOutputNode(ResizableInputNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_PLOT_HISTOGRAM
    op_title = "Histogram"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.insockets    = []
        self.all_names = []
        self.c = 0
        self.input_socket_position  = LEFT_TOP
        self.convex  = ConvexHull2D()

    def onInputChange(self, new_edge=None):
        self.content.changed.emit()

    def resize(self):
        pass

    def initInnerClasses(self):
        self.content    = GraphicsOutputContent(self)
        self.grNode     = GraphicsOutputGraphicsNode(self)
        self.properties = HistogramProperties(self)
        self.content.changed.connect(self.recalculateNode)


    def prepareSettings(self):
        return True

    def prepareCanvas(self):
        self.all_names = []
        if not self.hasValue(0) : return

        value = self.getInput(0).value

        x_name = list(value.keys())[0]
        self.x_val  = value[x_name]

        if self.properties.xtitle == "":
            self.content.axes.set_xlabel(x_name)
        else:
            self.content.axes.set_xlabel(self.properties.xtitle)

        if self.properties.grid_main:
            self.content.axes.grid(visible=True, which="major")
        else:
            self.content.axes.grid(visible=False, which="major")

        if self.properties.grid_minor:
            self.content.axes.grid(visible=True, which="minor")
        else:
            self.content.axes.grid(visible=False, which="minor")

        self.content.axes.set_ylabel(self.properties.ytitle)
        self.content.axes.xaxis.label.set_size( self.properties.labelsize )
        self.content.axes.yaxis.label.set_size( self.properties.labelsize )

        self.content.axes.tick_params(labelsize= self.properties.ticksize)
        self.content.axes.tick_params(labelsize= self.properties.ticksize)

        self.content.axes.set_xlim(self.properties.x_limit_min, self.properties.x_limit_max)
        self.content.axes.set_ylim(self.properties.y_limit_min, self.properties.y_limit_max)


    def addData(self, value):
        # if no input then return
        if not value : return 

        # update the input
        for name in value:
            # name is not in the properties 
            if name not in self.content.items : continue
            if name not in self.all_names : self.all_names.extend([name])

            # update the styles
            dat = np.histogram(value[name], int(self.properties.bins.text()))
            y   = np.repeat(dat[0], 2)
            x   = np.repeat(dat[1], 2)[1:-1]
            self.updateData(name, x, y)
            self.updateStyle(name)
        
        # add what is missing
        for name in value:
            # name is in the properties and has been already updated
            if name in self.content.items : continue
            if name not in self.all_names : self.all_names.extend([name])

            self.properties.appendDataWidget(name)
            dat = np.histogram(value[name], int(self.properties.bins.text()))
            y   = np.repeat(dat[0], 2)
            x   = np.repeat(dat[1], 2)[1:-1]
            self.content.items[name], = self.content.axes.plot(x, y, label=name, 
                                    color=self.properties.maincolor[name])#, bins=int(self.properties.bins.text()))
                                    #alpha=float(self.properties.alphas[name].text())

        # remove what is not in the values
        for name in list(self.content.items.keys()):
            # name is in the plot input and does not have to be removed
            if name in self.all_names : continue
            
            self.content.axes.hist.remove(self.content.items[name])

            del self.content.items[name]
            self.properties.removeWidget(name)
            self.content.canvas.draw()

            
    def updateData(self, name, x, y):
        self.content.items[name].set_xdata(x)
        self.content.items[name].set_ydata(y)

    def updateStyle(self, name):
        if name not in self.content.items : return

        self.content.items[name].set(label=name)
        self.content.items[name].set(color=self.properties.maincolor[name],
                                    alpha=float(self.properties.alphas[name].text()))
        self.content.canvas.draw()

    def getDataLimits(self):
        xmin  = 1.0e20
        xmax  =-1.0e20
        ymin  = 1.0e20
        ymax  =-1.0e20
        sxmin = 0.0
        sxmax = 0.0
        symin = 0.0
        symax = 0.0
        
        for input in self.insockets:
            if not input.value : return 0.0 * (1.0 - sxmin) + sxmin * xmin, 1.0 * (1.0 - sxmax) + sxmax * xmax, 0.0 * (1.0 - symin) + symin * ymin, 1.0 * (1.0 - symax) + symax * ymax

            for name in input.value:
                dat = np.histogram(input.value[name], int(self.properties.bins.text()))
                y   = np.repeat(dat[0], 2)
                x   = np.repeat(dat[1], 2)[1:-1]

                if np.any(x):
                    if min(x) < xmin : 
                        xmin  = min(x)
                        sxmin = 1.0
                    if max(x) > xmax : 
                        xmax  = max(x)
                        sxmax = 1.0

                    if not np.any(y): continue
                
                    if min(y) < ymin : 
                        ymin  = min(y)
                        symin = 1.0
                    
                    if max(y) > ymax : 
                        ymax  = max(y)
                        symax = 1.0
        
        return 0.0 * (1.0 - sxmin) + sxmin * xmin, 1.0 * (1.0 - sxmax) + sxmax * xmax, 0.0 * (1.0 - symin) + symin * ymin, 1.0 * (1.0 - symax) + symax * ymax


        
    def drawPlot(self):
        #self.content.axes.clear()
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


