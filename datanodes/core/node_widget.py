from datanodes.core.node_scene import Scene, InvalidFile
from datanodes.core.node_node import  Node
from datanodes.core.node_socket import Socket
from datanodes.core.node_edge import EDGE_BEZIER, Edge
import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsScene, QGraphicsView, QMessageBox, QVBoxLayout, QWidget
from datanodes.graphics.graphics_scene import GraphicsScene
from datanodes.graphics.graphics_view import GraphicsView
from PyQt5.QtCore import *

class NodeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None

        self.initUI()

    def initUI(self):

        # Define the layout and set its margins to 0 on all sides
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # create the scene
        self.scene = Scene()

        # create the view
        self.view = GraphicsView(self.scene, self)
        self.layout.addWidget(self.view)

    def isModified(self):
        return self.scene.isModified()

    def isFilenameSet(self):
        return self.filename is not None

    def hasSelectedItems(self):
        return self.getSelectedItems() != []

    def getSelectedItems(self):
        return self.scene.selectedItems()

    def canUndo(self):
        return self.scene.history.canUndo()

    def canRedo(self):
        return self.scene.history.canRedo()

    def getUserFriendlyFilename(self):
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Node-tree"
        return name + ("*" if self.isModified() else "")

    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.scene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.scene.addText("Hello there, guys!")
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1., 1., 1.))

    def addNodes(self):
        node1 = Node(self.scene, "First awesome node 1", inputs  = [1,1,1], outputs = [2])
        node2 = Node(self.scene, "First awesome node 2", inputs  = [1,1], outputs = [2, 3])
        node3 = Node(self.scene, "First awesome node 3", inputs  = [1,1,1], outputs = [2])
        node4 = Node(self.scene, "First awesome node 4", inputs  = [1,1,1], outputs = [2])

        node1.setPos(-200, -150)
        node2.setPos(-200,  150)
        node3.setPos( 200,  0)
        node4.setPos( 500,  -50)

        edge1 = Edge(self.scene, node1.outputs[0], node3.inputs[0])
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[1])

        self.scene.history.storeHistory("Initial state", setModified=False)

    def fileNew(self):
        """Empty the scene (create new file)"""
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()


    def fileLoad(self, file):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(file)
            self.filename = file
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            for node in self.scene.nodes:
                node.eval()
            return True

        except InvalidFile as e:
            print(e)
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading {0}".format(file), str(e))
            return False

        finally:
            QApplication.restoreOverrideCursor()
        
        return False

    def fileSave(self, filename=None):
        
        if filename is not None:
            self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True
