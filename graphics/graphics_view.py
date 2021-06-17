from core.node_edge import Edge
from graphics.graphics_edge import GraphicsEdge
from graphics.graphics_socket import GraphicsSocket
from typing import FrozenSet
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

MODE_NONE       = 1
MODE_EDGE_DRAG  = 2

DEBUG = True

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent = None):
        super().__init__(parent)

        self.grScene = scene.grScene

        self.initUI()

        self.setScene(self.grScene)

        self.mode = MODE_NONE

        self.drad_threshold = 10.0

        # general view settings
        # the zoom settings
        self.zoomInScale = 1.150
        self.zoomClamp   = True
        self.zoom        = 20.0
        self.zoomStep    = 1.0
        self.zoomRange   = [0.0, 40.0]

    def initUI(self):
        # set high quality of the view
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        

        # sets the translation so that while zooming it will
        # zoom to the point where the mouse is
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)


    # --------- Additional functions  ---------------

    def getItemAtClick(self, event):
        """ return the object above which the mouse was clicked """
        return self.itemAt( event.pos() )


    def clickClickDist(self, event):
        """ returns true if the mouse moved between the mouse click and the current event more
        then the threshold value set in the __init__ """
        self.new_lmb_click_pos = self.mapToScene(event.pos())
        dist = self.new_lmb_click_pos - self.last_lmb_click_pos
        dist = (dist.x()**2 + dist.y()**2)**0.5
        return dist > self.drad_threshold


    def edgeDragEnd(self, item):
        """ Ends the drag mouse event between two sockets """
        self.mode = MODE_NONE
        if DEBUG : print("End draging edge")

        if type(item) is GraphicsSocket:
            if DEBUG : print(" ASSIGN End socket")
            return True

        return False

    def edgeDragStart(self, item):
        if DEBUG : print ("View:edgeDragStart ~ Start the dragging ")
        if DEBUG : print ("View:edgeDragStart ~    assign the start socket to :", item.socket)
        self.dragEdge = Edge(self.grScene.scene, item.socket, None)
        if DEBUG : print ("View:edgeDragStart ~    dragEdge :", self.dragEdge)




    # ------- Remap the mouse press events to custom functions-------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)

        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)

        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)

        else:
            super().mousePressEvent(event)

    # Remap the mouse release events to custom functions
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)

        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)

        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)

        else:
            super().mouseReleaseEvent(event)


    # ------- Custom mouse events ----------------------

    def middleMouseButtonPress(self, event):
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        pressEvent = QMouseEvent(event.type(), 
                                 event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                 event.modifiers())
        super().mousePressEvent(pressEvent)

    
    def middleMouseButtonRelease(self, event):
        releaseEvent = QMouseEvent(event.type(), 
                                   event.localPos(), event.screenPos(),
                                   Qt.LeftButton, event.buttons() & -Qt.LeftButton,
                                   event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.NoDrag)


    def leftMouseButtonPress(self, event):
        item = self.getItemAtClick(event)
        self.last_lmb_click_pos = self.mapToScene(event.pos())


        if type(item) is GraphicsSocket:
            print("Socket was clicked")
            if self.mode == MODE_NONE:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return
        
        if self.mode == MODE_EDGE_DRAG:

            # make sure that mouse moved above the threshold value
            res = self.edgeDragEnd(item)
            if res: return

        super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):

        # Get the item above which the mouse was released
        item = self.getItemAtClick(event)
        
        # check if the mode was EDGE_DRAG
        if self.mode == MODE_EDGE_DRAG:

            # make sure that mouse moved above the threshold value
            if self.clickClickDist(event):
                res = self.edgeDragEnd(item)
                if res: return

        super().mouseReleaseEvent(event)


    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)
        if DEBUG : 
            if type(item) is GraphicsSocket:
                print("RMB DEBUG : ", item.socket, "has edge :", item.socket.edge)

            if isinstance(item, GraphicsEdge):
                print("RMB DEBUG : ", item.edge, "  sockets : ", item.edge.start_socket, "<-->", item.edge.end_socket)

            if item is None:
                print("Scene: ")
                print("  Nodes : ")
                for node in self.grScene.scene.nodes : print("      ", node)
                print("  Edges : ")
                for edge in self.grScene.scene.edges : print("      ", edge)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)




    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.destination.setX(pos.x())
            self.dragEdge.grEdge.destination.setY(pos.y())
            self.dragEdge.grEdge.update()
        
        return super().mouseMoveEvent(event)




    def wheelEvent(self, event):
        # calculate the zoom value
        zoomOutScale = 1.0 / self.zoomInScale

        # calculate the zoom
        if event.angleDelta().y() > 0.0:
            zoomScale = self.zoomInScale
            self.zoom += self.zoomStep
        else:
            zoomScale = zoomOutScale
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom <= self.zoomRange[0]: 
            self.zoom, clamped = self.zoomRange[0], True


        if self.zoom >= self.zoomRange[1]: 
            self.zoom, clamped = self.zoomRange[1], True

        # set the scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomScale, zoomScale)

