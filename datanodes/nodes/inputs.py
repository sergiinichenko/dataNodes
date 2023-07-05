
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.core.node_settings import *
from datanodes.nodes.datanode import *
from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QLineEdit, QAction, QMenu
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QApplication

class ValueInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140
        self.height = 70

class ValueInputContent(DataContent):
    def initUI(self):
        super().initUI()
  
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)

        self.label = QLineEdit("x", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.value = QLineEdit("1.0", self)
        self.value.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.label, 0, 0)
        self.mainlayout.addWidget(self.value, 0, 1)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.value.text()
        res['label'] = self.label.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.value.setText(data['value'])
            self.label.setText(data['label'])
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_VALINPUT)
class ValueInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_VALINPUT
    op_title = "Value"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = ValueInputContent(self)
        self.grNode  = ValueInputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.value.returnPressed.connect(self.onInputChanged)
        self.content.label.returnPressed.connect(self.onInputChanged)
        self.content.changed.connect(self.recalculateNode)    
        
    def evalImplementation(self, silent=False):
        try:
            u_value = self.content.value.text()
            s_value = float(u_value)
            label   = self.content.label.text()
            self.getOutput(0).value = {label : s_value}
            self.getOutput(0).type  = "float"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            self.setInvalid()
            return False







class MultiValueInputGraphicsNode(AdjustableOutputGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200
        self.height = 100
        self.min_height = 100

class MultiValueInputContent(AdjustableOutputContent):
    def initUI(self):
        super().initUI()
        self.mainlayout.setSpacing(0)
        self.remove = {}
        self.labels = {}
        self.values = {}

    def appendPair(self, at=None):
        if self.labels and not at:
            i = len(self.labels)
        elif at:
            i = at
        else:
            i = 0
        
        id = str(int(np.random.rand()*1000000))
        while id in self.labels : id = str(int(np.random.rand()*1000000))

        self.remove[id]  = RemoveButton(self, id)
        self.labels[id]  = QLineEdit("x"+str(i), self)
        self.labels[id].setAlignment(Qt.AlignRight)
        self.values[id]  = QLineEdit("1.0", self)
        self.values[id].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.remove[id], i, 0)
        self.mainlayout.addWidget(self.labels[id], i, 1)
        self.mainlayout.addWidget(self.values[id], i, 2)

        self.labels[id].returnPressed.connect(self.node.recalculateNode)
        self.values[id].returnPressed.connect(self.node.recalculateNode)
        self.remove[id].clicked.connect(self.remove[id].removePair)


    def sortWidgets(self):
        for i, key in enumerate(self.labels):
            self.remove[key].setParent(None)
            self.labels[key].setParent(None)
            self.values[key].setParent(None)

        for i, key in enumerate(self.labels):
            self.mainlayout.addWidget(self.remove[key], i, 0)
            self.mainlayout.addWidget(self.labels[key], i, 1)
            self.mainlayout.addWidget(self.values[key], i, 2)

    def serialize(self):
        res     = super().serialize()
        labels  = []
        values  = []
        ids     = []
        for key in self.labels:
            labels.append(self.labels[key].text())
            values.append(self.values[key].text())
            ids.append(key)

        res['value'] = values
        res['label'] = labels
        res['id']    = ids
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            for i, id, label, value in zip(range(len(data['label'])), data['id'], data['label'], data['value']):
                self.remove[id]  = RemoveButton(self, id)
                self.labels[id]  = QLineEdit(label, self)
                self.labels[id].setAlignment(Qt.AlignRight)
                self.values[id]  = QLineEdit(value, self)
                self.values[id].setAlignment(Qt.AlignLeft)

                self.mainlayout.addWidget(self.remove[id], i, 0)
                self.mainlayout.addWidget(self.labels[id], i, 1)
                self.mainlayout.addWidget(self.values[id], i, 2)
                self.remove[id].clicked.connect(self.remove[id].removePair)
                self.labels[id].returnPressed.connect(self.node.recalculateNode)
                self.values[id].returnPressed.connect(self.node.recalculateNode)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_MULVALINPUT)
class MultiValueInputNode(AdjustableOutputNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_MULVALINPUT
    op_title = "Multi-Value"

    def __init__(self, scene, inputs=[], outputs=[SOCKET_TYPE_DATA]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()
        self.timer = None

    def initSettings(self):
        super().initSettings()
        self.socket_spacing = 25.0
        
    def onEdgeConnectionChanged(self, new_edge=None):
        self.recalculateNode()

    def initInnerClasses(self):
        self.content = MultiValueInputContent(self)
        self.grNode  = MultiValueInputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)
        self.content.addItems.clicked.connect(self.appendNewPair)

    def resize(self):
        try:
            size = len(self.content.labels)
            current_size  = (size-1) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin + 38.0
            padding_title = self.grNode.title_height + 2.0 * self.grNode.padding
            if current_size > self.grNode.min_height:
                self.grNode.height = current_size
                self.grNode.update()
                self.content.updateSize()
            self.scene.grScene.update()
        except Exception as e : pass
        

    def appendNewPair(self):
        self.content.appendPair()
        # The timer is set here
        self.timer = QTimer()
        self.timer.timeout.connect(self.resize)
        self.timer.start(1)


    def evalImplementation(self, silent=False):
        try:
            if self.getOutputs():
                self.value = {}
                for id in self.content.values:
                    value = float(self.content.values[id].text())
                    label = self.content.labels[id].text()
                    self.value[label] = value

                self.getOutput(0).value = self.value
                self.getOutput(0).type  = "df"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            self.setInvalid()
            return False








class TableInputGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 340
        self.height = 300

class TableInputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.mainWidget = QTableWidget(self)
        self.mainWidget.setRowCount(10)
        self.mainWidget.setColumnCount(3)
        self.mainWidget.installEventFilter(self)
        self.layout.addWidget(self.mainWidget)

        for row in range(10):
            for col in range(3):
                item = QTableWidgetItem("")
                self.mainWidget.setItem(row, col, item)
                
        self.mainWidget.keyPressEvent     = self.tableOnKeyPressEvent
        self.mainWidget.mouseReleaseEvent = self.onMouseReleaseEvent
    
    
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.ContextMenu and source is self.mainWidget:
            menu = QMenu()
            pasteData = QAction(self)
            pasteData.setText("Paste data")
            pasteDataAct = menu.addAction(pasteData)

            copySelected = QAction(self)
            copySelected.setText("Copy selected")
            copySelectedAct = menu.addAction(copySelected)

            copyAll = QAction(self)
            copyAll.setText("Copy all")
            copyAllAct = menu.addAction(copyAll)

            clearTable = QAction(self)
            clearTable.setText("Clear table")
            clearTableAct = menu.addAction(clearTable)

            action    = menu.exec_(self.mapToGlobal(event.pos()))
            if action == pasteData    : self.pasteDataFromClipboard()
            if action == copySelected : self.copyDataToClipboard(all = False)
            if action == copyAll      : self.copyDataToClipboard(all = True)
            if action == clearTable   : self.clearTable()

            #if menu.exec_(event.globalPos()):
            #    item = source.itemAt(event.pos())
            #    print(item.text())
            return True
        return super().eventFilter(source, event)
        
    def clearTable(self):
        while self.mainWidget.rowCount() > 0:
            self.mainWidget.removeRow(0)
        
        self.mainWidget.setRowCount(10)
        self.mainWidget.setColumnCount(3)
        for row in range(10):
            for col in range(3):
                item = QTableWidgetItem("")
                self.mainWidget.setItem(row, col, item)
        self.node.recalculateNode()        

    
    def copyDataToClipboard(self, all=False):
        if all:
            data = ""
            for row in range(self.mainWidget.rowCount()):
                for col in range(self.mainWidget.columnCount()):
                    if self.mainWidget.item(row, col) is not None:
                        data  = data + self.mainWidget.item(row, col).text() + ("\t" if col < (self.mainWidget.columnCount()-1) else "")
                    else : 
                        data  = data + ","
                data = data + "\n"
        else:
            if len(self.mainWidget.selectedIndexes()) == 0 : return False
            data  = ""
            cr    = self.mainWidget.selectedIndexes()[0].row()
            first = True
            for item in self.mainWidget.selectedIndexes():
                if not first:                
                    if cr == item.row(): 
                        data = data + "\t"
                    else:
                        data = data + "\n"
                        cr   = item.row()
                data = data + self.mainWidget.item(item.row(), item.column()).text()
                first = False

        QApplication.instance().clipboard().setText(data)
        return         
        
        
    def pasteDataFromClipboard(self):
        try:
            data = QApplication.instance().clipboard().text()
            current = self.mainWidget.currentIndex()
            row     = current.row()
            for line in iter(data.splitlines()):
                col = current.column()
                if row >= self.mainWidget.rowCount():
                    self.mainWidget.insertRow(row)
                if col >= self.mainWidget.columnCount():
                    self.mainWidget.insertColumn(col)

                for val in iter(line.split("\t")):
                    if self.mainWidget.item(row, col) is not None:
                        self.mainWidget.item(row, col).setText(val)
                    else:
                        item = QTableWidgetItem(val)
                        self.mainWidget.setItem(row, col, item)
                    col+=1
                row+=1
            self.node.recalculateNode()        
        
        except Exception as e: 
            dumpException (e)
            self.node.e = e
            self.node.setInvalid()
       
                            
    def tableOnKeyPressEvent(self, event):
        current = self.mainWidget.currentIndex()

        # custom return press event listener
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # pass on the keyPressEvent to the table
            QTableWidget.keyPressEvent(self.mainWidget, event) 
            nextIndex = current.sibling(current.row() + 1, current.column())
            if nextIndex.isValid():
                self.mainWidget.setCurrentIndex(nextIndex)
                self.mainWidget.edit(nextIndex)
            self.node.recalculateNode()
            # do what needs to be done here
            # you can return here if you do not want to pass on the return to the table
            return

        if event.key() == Qt.Key_Delete:
            # pass on the keyPressEvent to the table
            QTableWidget.keyPressEvent(self.mainWidget, event) 
            for item in self.mainWidget.selectedItems():
                if item is not None : item.setText("")
            self.node.recalculateNode()
            # do what needs to be done here
            # you can return here if you do not want to pass on the return to the table
            return

        if event.key() == Qt.Key_Down:
            nextRow = current.sibling(current.row() + 1, current.column())
            row = current.row() + 1
            if not nextRow.isValid():
                self.mainWidget.insertRow(self.mainWidget.rowCount())
                nextRow = current.sibling(row, current.column())
            self.mainWidget.setCurrentIndex(nextRow)
            return

        if event.key() == Qt.Key_Right:
            nextCol = current.sibling(current.row(), current.column() + 1)
            col = current.column() + 1
            if not nextCol.isValid():
                self.mainWidget.insertColumn(self.mainWidget.columnCount())
                nextCol = current.sibling(current.row(), col)
            self.mainWidget.setCurrentIndex(nextCol)
            return

        # pass on the keyPressEvent to the table
        QTableWidget.keyPressEvent(self.mainWidget, event) 


    def onMouseReleaseEvent(self, event):
        QTableWidget.mouseReleaseEvent(self.mainWidget, event) 
        self.node.scene._selected_contents = self
        self.node.scene.grScene.itemSelected.emit()            
            
            
    def onCopy(self):
        if len(self.mainWidget.selectedIndexes()) == 0 : return False
        data  = ""
        cr    = self.mainWidget.selectedIndexes()[0].row()
        first = True
        for item in self.mainWidget.selectedIndexes():
            if not first:                
                if cr == item.row(): 
                    data = data + "\t"
                else:
                    data = data + "\n"
                    cr   = item.row()
            data = data + self.mainWidget.item(item.row(), item.column()).text()
            first = False
            #QApplication.instance().clipboard().setText(data)
        return data


    def onPaste(self, data):
        current = self.mainWidget.currentIndex()
        row     = current.row()
        for line in iter(data.splitlines()):
            col = current.column()
            if row >= self.mainWidget.rowCount():
                self.mainWidget.insertRow(row)

            for val in iter(line.split("\t")):
                if self.mainWidget.item(row, col) is not None:
                    self.mainWidget.item(row, col).setText(val)
                else:
                    item = QTableWidgetItem(val)
                    self.mainWidget.setItem(row, col, item)
                col+=1
            row+=1
        self.node.recalculateNode()
    
    def serialize(self):
        res = super().serialize()
        res['width']  = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['cols'] = self.mainWidget.columnCount()
        res['rows'] = self.mainWidget.rowCount()
        
        rows = self.mainWidget.rowCount()
        cols = self.mainWidget.columnCount()
        values = []
        for c in range(cols):
            for r in range(0, rows):
                if self.mainWidget.item(r, c) is not None:
                    if self.mainWidget.item(r, c).text() != "":
                        record = {"c" : c, "r" : r, "d" : self.mainWidget.item(r, c).text()}
                        values.append(record)
        res['values'] = values
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                values = data['values']
                for val in values:
                    row = val["r"]
                    col = val["c"]
                    vtx = val["d"]
                    if col >= self.mainWidget.columnCount():
                        self.mainWidget.insertColumn(col)
                    if row >= self.mainWidget.rowCount():
                        self.mainWidget.insertRow(row)

                    if self.mainWidget.item(row, col) is not None:
                        self.mainWidget.item(row, col).setText(vtx)
                    else:
                        item = QTableWidgetItem(vtx)
                        self.mainWidget.setItem(row, col, item)
                """
                for val in values:
                    self.mainWidget.item(val["r"], val["c"]).setText(val["d"])
                """
                self.updateSize()
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_TABLEINPUT)
class TableInputNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_TABLEINPUT
    op_title = "Table"

    def __init__(self, scene, inputs=[], outputs=[SOCKET_TYPE_DATA]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.output_socket_position  = RIGHT_TOP


    def initInnerClasses(self):
        self.content    = TableInputContent(self)
        self.grNode     = TableInputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.mainWidget.openPersistentEditor

    def updateNames(self, dict):
        for c, key in enumerate(self.value):
            print(c, key)
            item = QTableWidgetItem(key)
            self.content.mainWidget.setItem(0, c, item)


    def readTable(self):
        print("READ TABLE")
        rows = self.content.mainWidget.rowCount()
        cols = self.content.mainWidget.columnCount()
        self.value.clear()
        
        for c in range(cols):
            if self.content.mainWidget.item(0, c) is None : continue
            
            name = self.content.mainWidget.item(0, c).text()
            if name != "":
                vals = []
                for r in range(1, rows):
                    if self.content.mainWidget.item(r, c) is not None:
                        if not self.isString(self.content.mainWidget.item(r, c).text()):
                            val = float(self.content.mainWidget.item(r, c).text())
                            vals.extend([val])
                self.value[name] = vals


    def evalImplementation(self, silent=False):
        try:
            if self.getOutputs():
                self.value = {}
                self.readTable()
                self.getOutput(0).value = self.value
                self.getOutput(0).type  = "df"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            self.setInvalid()
            return False

