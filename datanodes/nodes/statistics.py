from pandas.core.algorithms import isin
from pandas.core.frame import DataFrame
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *


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








