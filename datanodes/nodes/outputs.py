from PyQt5.QtCore import QEvent, QObject
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPlainTextEdit, QSizePolicy
from PyQt5.QtWidgets import QAction, QMenu, QGraphicsProxyWidget
from PyQt5.QtWidgets import QApplication

class TableOutputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200
        self.height = 200

class TableOutputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.table.setRowCount(3)
        self.table.setColumnCount(3)
        self.table.installEventFilter(self)
        self.layout.addWidget(self.table)
        
        self.table.mouseReleaseEvent = self.onMouseReleaseEvent

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.ContextMenu and source is self.table:
            menu = QMenu()
            copySelected = QAction(self)
            copySelected.setText("Copy selected")
            copyDataAct = menu.addAction(copySelected)

            copyAll = QAction(self)
            copyAll.setText("Copy all")
            copyAllAct = menu.addAction(copyAll)

            action    = menu.exec_(self.mapToGlobal(event.pos()))
            if action == copySelected : self.copyDataToClipboard(all = False)
            if action == copyAll      : self.copyDataToClipboard(all = True)

            #if menu.exec_(event.globalPos()):
            #    item = source.itemAt(event.pos())
            #    print(item.text())
            return True
        return super().eventFilter(source, event)
    
    def copyDataToClipboard(self, all=False):
        if all:
            data = ""
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    if self.table.item(row, col) is not None:
                        data  = data + self.table.item(row, col).text() + ("\t" if col < (self.table.columnCount()-1) else "")
                    else : 
                        data  = data + ","
                data = data + "\n"
        else:
            if len(self.table.selectedIndexes()) == 0 : return False
            data  = ""
            cr    = self.table.selectedIndexes()[0].row()
            first = True
            for item in self.table.selectedIndexes():
                if not first:                
                    if cr == item.row(): 
                        data = data + "\t"
                    else:
                        data = data + "\n"
                        cr   = item.row()
                data = data + self.table.item(item.row(), item.column()).text()
                first = False

        QApplication.instance().clipboard().setText(data)
            
        return 
    
    def onMouseReleaseEvent(self, event):
        QTableWidget.mouseReleaseEvent(self.table, event) 
        self.node.scene._selected_contents = self
        self.node.scene.grScene.itemSelected.emit()            


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

@register_node(OP_MODE_TABLEOUTPUT)
class TableOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_TABLEOUTPUT
    op_title = "Table"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP


    def initInnerClasses(self):
        self.content    = TableOutputContent(self)
        self.grNode     = TableOutputGraphicsNode(self)
        self.properties = NodeProperties(self)

    def isString(self, x):
        try:
            float(x)
            return False
        except:
            return True

    def updateNames(self, dict):
        for c, key in enumerate(self.value):
            print(c, key)
            item = QTableWidgetItem(key)
            self.content.table.setItem(0, c, item)

    def fillTable(self):
        self.content.table.clear()
        self.content.table.setRowCount(0)
        self.content.table.setColumnCount(0)
        
        if self.value is None : return

        nofrows = 1
        for key in self.value:

            if isinstance(self.value[key], (list, np.ndarray)):
                if len(self.value[key]) > nofrows : nofrows = len(self.value[key])

        self.content.table.setColumnCount(len(self.value))
        self.content.table.setRowCount(nofrows+1)

        for c, key in enumerate(self.value):
            item = QTableWidgetItem(key)
            self.content.table.setItem(0, c, item)
            
            if isinstance(self.value[key], (list, np.ndarray)):
                for r, value in enumerate(self.value[key]):
                    item = QTableWidgetItem(self.getFormatedValue(value))
                    self.content.table.setItem(r+1, c, item)
            else:
                item = QTableWidgetItem(self.getFormatedValue(self.value[key]))
                self.content.table.setItem(1, c, item)

    def evalImplementation(self, silent=False):
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
            self.fillTable()
            if input_edge.type == "df":
                self.table.setRowCount(self.value.shape[0])
                self.table.setColumnCount(self.value.shape[1])
                #self.table.
            return True








class TextOutputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200
        self.height = 200

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
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.textOut.clear()
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.updateSize()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_TEXTOUTPUT)
class TextOutputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_TEXTOUTPUT
    op_title = "Text"

    def __init__(self, scene, inputs=[1], outputs=[]):
        super().__init__(scene, inputs, outputs)


    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP

    def updateNames(self, dict):
        self.content.textOut.clear()
        self.content.textOut.insertPlainText(str(self.value))

    def initInnerClasses(self):
        self.content = TextOutputContent(self)
        self.grNode  = TextOutputGraphicsNode(self)
        self.properties = NodeProperties(self)


    def evalImplementation(self, silent=False):
        input_edge = self.getInput(0)
        if not input_edge:
            if DEBUG : print("OUTNODE_TXT: no input edge")
            self.setInvalid()
            if DEBUG : print("OUTNODE_TXT: set invalid")
            self.e = "Does not have and intry Node"
            self.content.textOut.clear()
            self.content.textOut.insertPlainText("NaN")
            if DEBUG : print("OUTNODE_TXT: clear the content")
            return False
        else:            
            if DEBUG : print("OUTNODE_TXT: process the input edge data")
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("OUTNODE_TXT: reset Dirty and Invalid")
            self.e = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            self.content.textOut.clear()
            if DEBUG : print("OUTNODE_TXT: get the value and type and clear the content")
            if isinstance(self.value, dict):
                if DEBUG : print("OUTNODE_TXT: DF input datatype")
                for key in self.value:
                    self.content.textOut.insertPlainText(key + " = " + str(self.value[key]) + "\n")
                if DEBUG : print("OUTNODE_TXT: DF content was set")
            elif isinstance(self.value, pd.DataFrame):
                if DEBUG : print("OUTNODE_TXT: DF input datatype")
                self.content.textOut.insertPlainText(self.value.to_markdown())
                if DEBUG : print("OUTNODE_TXT: DF content was set")
            else:
                if DEBUG : print("OUTNODE_TXT: other format of the input")
                try:
                    self.content.textOut.insertPlainText(str(self.value))
                except Exception as e : 
                    dumpException(e)
                    self.content.textOut.insertPlainText("NaN")
                    return False
            return True






