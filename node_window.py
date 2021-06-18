from core.node_scene import Scene
from core.node_node import  Node
from core.node_socket import Socket
from core.node_edge import EDGE_BEZIER, Edge

from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QVBoxLayout, QWidget
from graphics.graphics_scene import GraphicsScene
from graphics.graphics_view import GraphicsView
from PyQt5.QtCore import *

class NodeWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        # Define the location and size of the window
        self.setGeometry(200, 100, 1000, 800)

        # Define the layout and set its margins to 0 on all sides
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # create the scene
        self.scene = Scene()
        # self.scene = self.scene.grScene

        self.addNodes()

        # create the view
        self.view = GraphicsView(self.scene, self)
        self.layout.addWidget(self.view)


        self.setWindowTitle("Node editor")
        self.show()

        # self.addDebugContent()


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
