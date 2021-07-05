from datanodes.core.utils import dumpException
from datanodes.graphics.graphics_cutline import GraphicsCutLine
from datanodes.core.node_node import SOCKET_INPUT, SOCKET_OUTPUT
from datanodes.core.node_edge import Edge
from datanodes.graphics.graphics_edge import GraphicsEdge
from datanodes.graphics.graphics_socket import GraphicsSocket
from datanodes.graphics.graphics_node import GraphicsNode
from typing import FrozenSet
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

MODE_NONE       = 1
MODE_EDGE_DRAG  = 2
MODE_DRAG_RESIZE = 3

MODE_EDGE_CUT   = 3

DEBUG = False

class GraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, scene, parent = None):
        super().__init__(parent)

        self.grScene = scene.grScene

        self.initUI()

        self.setScene(self.grScene)

        self.mode = MODE_NONE
        self.rubberBandDraggingRect = False

        self.drad_threshold = 10.0

        # general view settings
        # the zoom settings
        self.zoomInScale = 1.150
        self.zoomClamp   = True
        self.zoom        = 20.0
        self.zoomStep    = 1.0
        self.zoomRange   = [0.0, 40.0]

        self.cutline     = GraphicsCutLine()
        self.grScene.addItem(self.cutline)

        self._drap_enter_listeners = []
        self._drop_listeners = []
        #self.setContextMenuPolicy(Qt.NoContextMenu)

    def initUI(self):
        # set high quality of the view
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        

        # sets the translation so that while zooming it will
        # zoom to the point where the mouse is
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        for callback in self._drap_enter_listeners : callback(event)

    def dropEvent(self, event):
        for callback in self._drop_listeners : callback(event)

    def addDragEnterListener(self, callback):
        self._drap_enter_listeners.append(callback)

    def addDropListener(self, callback):
        self._drop_listeners.append(callback)




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

    def edgeDragStart(self, item):
        try:
            if DEBUG : print ("View:edgeDragStart ~ Start the dragging ")
            if DEBUG : print ("View:edgeDragStart ~    assign the start socket to :", item.socket)
            if DEBUG : print ("View:edgeDragStart ~    type of the socket :", item.socket.inout)

            self.drag_start_socket = item.socket
            self.drag_edge = Edge(self.grScene.scene, item.socket, None)
            if DEBUG : print ("View:edgeDragStart ~    drag_edge :", self.drag_edge)
        except Exception as e : dumpException(e)

    def edgeDragEnd(self, item):
        """ Ends the drag mouse event between two sockets """
        self.mode = MODE_NONE
        self.drag_edge.remove()
        if DEBUG : print("End draging edge")

        try:
            if type(item) is GraphicsSocket:

                # cannot connect the socket to itself
                if item.socket == self.drag_start_socket:
                    if DEBUG : print("View:edgeDragEnd ~ Cannot assign socket to itself")
                    return

                # cannot connect two sockets of the same type
                if item.socket.inout == self.drag_start_socket.inout:
                    if DEBUG : print("View:edgeDragEnd ~ Cannot assign two sockets of the same type")
                    return

                """ remove the edge if the socket is attached to an input socket
                and the socket already has an edge """
                if item.socket.inout == SOCKET_INPUT:
                    item.socket.clearEdges()
                    if DEBUG : print("View:edgeDragEnd ~ previous edge has been removed from the end socket")

                # cannot connect the socket to itself
                if self.drag_start_socket.inout == SOCKET_INPUT and self.drag_start_socket.hasEdge():
                    self.drag_start_socket.clearEdges()
                    if DEBUG : print("View:edgeDragEnd ~ Cannot assign socket to itself")


                """ remove the previous edge if there is one """
                new_edge = Edge(self.grScene.scene, self.drag_start_socket, item.socket)
                if DEBUG : print("View:edgeDragEnd ~ Created the new adge ")

                for socket in [self.drag_start_socket, item.socket]:
                    socket.node.onEdgeConnectionChanged(new_edge)
                    if socket.inout == SOCKET_INPUT : socket.node.onInputChanged(new_edge)
                    

                self.grScene.scene.history.storeHistory("created new edge")
                return True 
        except Exception as e : dumpException(e)

        if DEBUG : print("View:edgeDragEnd ~ The socket was not assigned and is removed")
        return False



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
        self.setDragMode(QGraphicsView.RubberBandDrag)


    def leftMouseButtonPress(self, event):
        # get item which we clicked on
        item = self.getItemAtClick(event)

        # we store the position of last LMB click
        self.last_lmb_click_pos = self.mapToScene(event.pos())

        # logic
        if hasattr(item, "node") or isinstance(item, GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return


        if type(item) is GraphicsSocket:
            if self.mode == MODE_NONE:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return

        super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):
        # get item which we release mouse button on
        item = self.getItemAtClick(event)

        # logic
        if hasattr(item, "node") or isinstance(item, GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.clickClickDist(event):
                res = self.edgeDragEnd(item)
                if res: return

        if self.mode == MODE_EDGE_CUT:
            self.cutInersectingEdges()
            self.cutline.points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NONE
            return

        super().mouseReleaseEvent(event)



    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)

        if DEBUG:
            if isinstance(item, GraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets:',
                                            item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is GraphicsSocket: print('RMB DEBUG:', item.socket, 'has edge:', item.socket.edge)

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)


    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)


    def cutInersectingEdges(self):

        for ix in range(len(self.cutline.points) - 1):
            p1 = self.cutline.points[ix]
            p2 = self.cutline.points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.grScene.scene.history.storeHistory("cut edges")


    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.grEdge.destination.setX(pos.x())
            self.drag_edge.grEdge.destination.setY(pos.y())
            self.drag_edge.grEdge.update()
        
        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.points.append(pos)
            self.cutline.update()

        self.last_scene_mouse_position = self.mapToScene(event.pos())
        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()),
            int(self.last_scene_mouse_position.y()))

        return super().mouseMoveEvent(event)


    def keyPressEvent(self, event):
        """
        if event.key() == Qt.Key_Delete:
            # Check if any items were selected in the scene
            if len(self.grScene.selectedItems()) > 0:
                # Delete the elements if items were selected
                self.deleteSelectedItem()
            else:
                # otherwise run the delete event
                super().keyPressEvent(event)

        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.grScene.scene.saveToFile("graph.json")

        elif event.key() == Qt.Key_O and event.modifiers() & Qt.ControlModifier:
            self.grScene.scene.loadFromFile("graph.json")


        # the undo Ctrl+Z key pressed
        elif event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier) and not (event.modifiers() & Qt.ShiftModifier):
            self.grScene.scene.history.undo()
        
        # the redo Ctrl+Shift+Z key pressed
        elif event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier) and (event.modifiers() &  Qt.ShiftModifier):
            self.grScene.scene.history.redo()

        elif event.key() == Qt.Key_H:
            print("HISTORY: len({0})".format(len(self.grScene.scene.history.history_stack)),
            " --- current step:", self.grScene.scene.history.history_current_step)
            print(self.grScene.scene.history.history_stack)


        else:"""
        super().keyPressEvent(event)

    def deleteSelectedItem(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, GraphicsEdge):
                item.edge.remove()
            elif isinstance(item, GraphicsNode):
                item.node.remove()
        self.grScene.scene.history.storeHistory("delete selected")


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

