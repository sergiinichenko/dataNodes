from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class ValueOutputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 120.0
        self.height = 80.0

class ValueOutputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setReadOnly(True)
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

@register_node(OP_MODE_VALOUTPUT)
class ValueOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_VALOUTPUT
    op_title = "Output value"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = ValueOutputContent(self)
        self.grNode  = ValueOutputGraphicsNode(self)


    def evalImplementation(self):
        input_edge = self.getInput(0)
        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.content.edit.setText("NaN")
            return False
        else:            
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            self.value = input_edge.value
            if self.value < 1000.0:
                self.content.edit.setText("{0:.3f}".format(self.value))
            elif self.value > 1000.0 and self.value < 100000.0:
                self.content.edit.setText("{0:.2f}".format(self.value))
            else:
                self.content.edit.setText("{0:.1f}".format(self.value))
            return True









class TableOutputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 200.0

class TableOutputContent(DataContent):
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
        #res['value'] = self.table.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            #self.table.setText(value)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_TABLEOUTPUT)
class TableOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_TABLEOUTPUT
    op_title = "Output table"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = TableOutputContent(self)
        self.grNode  = TableOutputGraphicsNode(self)


    def evalImplementation(self):
        input_edge = self.getInput(0)
        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.content.edit.setText("NaN")
            return False
        else:            
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            if input_edge.type == "df":
                self.table.setRowCount(self.value.shape[0])
                self.table.setColumnCount(self.value.shape[1])
                #self.table.
                print(self.value)                
            return True








class TextOutputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 200.0

class TextOutputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.textOut = QPlainTextEdit(self)
        self.textOut.setReadOnly(True)
        self.textOut.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.textOut)


    def serialize(self):
        res = super().serialize()
        res['value'] = self.textOut.toPlainText()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.textOut.clear()
            self.textOut.insertPlainText(value)
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.resize(data['content-widht'], data['content-height'])
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_TEXTOUTPUT)
class TextOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_TEXTOUTPUT
    op_title = "Output text"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initInnerClasses(self):
        self.content = TextOutputContent(self)
        self.grNode  = TextOutputGraphicsNode(self)


    def evalImplementation(self):
        input_edge = self.getInput(0)
        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.content.textOut.clear()
            self.content.textOut.insertPlainText("NaN")
            return False
        else:            
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            self.content.textOut.clear()
            if self.type == "df":
                self.content.textOut.insertPlainText(self.value.to_string())
            else:
                self.content.textOut.insertPlainText(str(self.value))
            return True






