from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datanodes.core.utils import *
from datanodes.core.main_conf import *

class NodeListBox(QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.initUI()

    def initUI(self):
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()


    def addMyItems(self):
        keys = list(DATA_NODES.keys())
        keys.sort()
        
        for key in keys:
            node = getClassFromOpCode(key)
            self.addMyItem(node.op_title, node.icon, node.op_code)

    def addMyItem(self, name, icon=None, op_code=0):
        item   = QListWidgetItem(name, self)
        pixmap = QPixmap(icon if icon is not None else '.')
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)


    def startDrag(self, *args, **kvargs):

        try:
            item    = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)

            pixmap  = QPixmap(item.data(Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e : dumpException(e)


class NodesDock(QDockWidget):
    def __init__(self, name, parent = None):
        super().__init__(name, parent=parent)

        self.initUI()

    def initUI(self):
        self.nodesListWidget = NodeListBox()
        self.setWidget(self.nodesListWidget)
        self.setFloating(False)
        self.setMinimumWidth(200)
        self.hide()
