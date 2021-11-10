from pandas.core.algorithms import isin
from pandas.core.frame import DataFrame
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt


class DescribeGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 200.0

class DescribeContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.table.setRowCount(3)
        self.table.setColumnCount(3)
        self.layout.addWidget(self.table)

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

@register_node(OP_STAT_DESCRIBE)
class DescribeOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_STAT_DESCRIBE
    op_title = "Describe"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)


    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP


    def initInnerClasses(self):
        self.content = DescribeContent(self)
        self.grNode  = DescribeGraphicsNode(self)
        self.properties = NodeProperties(self)

    def getFormatedValue(self, value):
        if np.abs(value) > 1000000.0:
            return "{:.3e}".format(value)
        if np.abs(value) > 1000.0 and np.abs(value) <= 1000000.0:
            return "{:.3e}".format(value)
        if np.abs(value) > 100.0 and np.abs(value) <= 1000.0:
            return "{:.2f}".format(value)
        if np.abs(value) > 1.0 and np.abs(value) <= 100.0:
            return "{:.3f}".format(value)
        if np.abs(value) > 0.01 and np.abs(value) <= 1.0:
            return "{:.4f}".format(value)
        if np.abs(value) > 0.00 and np.abs(value) <= 0.01:
            return "{:.3e}".format(value)
        else:
            return "{:.1f}".format(value)


    def fillTable(self):
        self.content.table.clear()
        self.content.table.setRowCount(11+1)
        self.content.table.setColumnCount(len(self.value)+1)
        font = QFont()
        font.setBold(True)
        print(font)

        # Fill the frame of the talbe (header and index column)
        for c, key in enumerate(self.value):
            item = QTableWidgetItem(key)
            item.setFont(font)
            self.content.table.setItem(0, c+1, item)
        for r, key in enumerate(["count", "mean", "median", "mode", "min", "Q1", "Q2", "Q3", "max", "skew", "std"]):
            item = QTableWidgetItem(key)
            item.setFont(font)
            self.content.table.setItem(r+1, 0, item)


        # Fill the table with data
        for c, key in enumerate(self.value):
            col = c+1
            # count
            item = QTableWidgetItem(str(self.value[key].size))
            self.content.table.setItem(1, col, item)

            # mean
            item = QTableWidgetItem(self.getFormatedValue(np.mean(self.value[key])))
            self.content.table.setItem(2, col, item)

            # median
            item = QTableWidgetItem(self.getFormatedValue(np.median(self.value[key])))
            self.content.table.setItem(3, col, item)

            # mode
            vals,counts = np.unique(self.value[key], return_counts=True)
            index = np.argmax(counts)
            item = QTableWidgetItem(self.getFormatedValue(vals[index]))
            self.content.table.setItem(4, col, item)

            # min
            item = QTableWidgetItem(self.getFormatedValue(np.min(self.value[key])))
            self.content.table.setItem(5, col, item)

            # Q1 percentile
            item = QTableWidgetItem(self.getFormatedValue(np.percentile(self.value[key], 25)))
            self.content.table.setItem(6, col, item)

            # Q2 percentile
            item = QTableWidgetItem(self.getFormatedValue(np.percentile(self.value[key], 50)))
            self.content.table.setItem(7, col, item)

            # Q3 percentile
            item = QTableWidgetItem(self.getFormatedValue(np.percentile(self.value[key], 75)))
            self.content.table.setItem(8, col, item)

            # max
            item = QTableWidgetItem(self.getFormatedValue(np.max(self.value[key])))
            self.content.table.setItem(9, col, item)

            # skew
            n = self.value[key].size
            mean  = np.mean(self.value[key])
            diff  = self.value[key] - mean
            sum2  = np.sum(diff**2.0)/n
            sum3  = np.sum(diff**3.0)/n

            skew  = sum3 / sum2**(3./2.)
            item = QTableWidgetItem(self.getFormatedValue(skew))
            self.content.table.setItem(10, col, item)

            # std
            item = QTableWidgetItem(self.getFormatedValue(np.std(self.value[key])))
            self.content.table.setItem(11, col, item)


    def evalImplementation(self, silent=False):
        input_edge = self.getInput(0)
        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.content.edit.setText("NaN")
            return False
        else:            
            try:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = input_edge.value
                self.type  = input_edge.type
                self.fillTable()
                return True

            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = e
                self.getOutput(0).value = {}
                self.getOutput(0).type = "float"
                return False








class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(self.axes)
        self.bar = divider.append_axes("right", size="5%", pad=0.05)

        super(MplCanvas, self).__init__(self.fig)



class CrossCorrelationGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300.0
        self.height = 300.0

class CrossCorrelationContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # graph area
        #self.graph = Figure()
        #self.graph.autofmt_xdate()
        #self.axis   = self.graph.add_subplot(111)
        #self.axis   = self.graph.add_axes([0., 0., 0.8, 0.8])
        self.canvas = MplCanvas()
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

@register_node(OP_STAT_CROSSCORRPLOT)
class CrossCorrelationNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_STAT_CROSSCORRPLOT
    op_title = "Correlation Heatmap"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = CrossCorrelationContent(self)
        self.grNode  = CrossCorrelationGraphicsNode(self)
        self.properties = NodeProperties(self)


    def prepareSettings(self):
        return True


    def drawPlot(self):
        self.content.canvas.axes.clear()

        size  = len(self.value)
        names = list(self.value.keys())

        nofelems = 0
        for key in self.value:
            if isinstance(self.value[key], (np.ndarray)):
                if len(self.value[key]) > nofelems : nofelems = len(self.value[key])


        data = np.empty((0, nofelems))
        for key in self.value:
            data = np.append(data, [self.value[key]], axis=0)
        corr = np.corrcoef(data)

        im = self.content.canvas.axes.imshow(corr, vmin = -1.0, vmax = 1.0)
        plt.colorbar(im, cax=self.content.canvas.bar)
        #bar = self.content.canvas.fig.colorbar(im)


        ticks = np.arange(0, size, 1)
        self.content.canvas.axes.set_xticks(ticks)
        self.content.canvas.axes.set_yticks(ticks)

        self.content.canvas.axes.set_xticklabels(names, rotation=60)
        self.content.canvas.axes.set_yticklabels(names)

        for i in range(size):
            for j in range(size):
                text = self.content.canvas.axes.text(j, i, np.round(corr[i, j], decimals=2),
                        ha='center', va='center', color='white')

        self.content.canvas.fig.tight_layout()
        self.content.canvas.draw()


    def evalImplementation(self, silent=False):
        if isinstance(self.value, dict):
            self.drawPlot()
        else:
            pass
        return True



