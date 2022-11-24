from datanodes.core.utils import dumpException
from datanodes.graphics.graphics_cutline import GraphicsCutLine
from datanodes.core.node_node import SOCKET_INPUT, SOCKET_OUTPUT
from datanodes.core.node_edge import Edge
from datanodes.core.node_edge_dragging import EdgeDragging
from datanodes.core.node_edge_rerouting import EdgeRerouting
from datanodes.core.node_edge_snapping import EdgeSnapping
from datanodes.core.node_edge_intersect import EdgeIntersect
from datanodes.graphics.graphics_edge import GraphicsEdge
from datanodes.graphics.graphics_socket import GraphicsSocket
from datanodes.graphics.graphics_node import GraphicsNode
from typing import FrozenSet
from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import pyqtSignal, QRectF, QPointF, QEvent, Qt
from PyQt5.QtGui import QPainter, QMouseEvent, QInputEvent

MODE_NONE        = 1
MODE_EDGE_DRAG   = 2
MODE_DRAG_RESIZE = 3
MODE_EDGE_REROUT = 4
MODE_EDGE_CUT    = 5
MODE_NODE_DRAG   = 6

STATE_STRING = ['', 'Noop', 'Edge Drag', 'Edge Cut', 'Edge Rerouting', 'Node Drag']

#: Socket snapping distance
EDGE_SNAPPING_RADIUS = 10
#: Enable socket snapping feature
EDGE_SNAPPING        = True

DEBUG                = False

class GraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, scene, parent = None):
        super().__init__(parent)

        self.grScene = scene.grScene

        self.initUI()

        self.setScene(self.grScene)

        self.mode        = MODE_NONE
        self.rubberBandDraggingRect = False

        self.drad_threshold = 10.0

        # Edge draging, rerouting and snapping instance
        self.dragging  = EdgeDragging(self)
        self.rerouting = EdgeRerouting(self)
        self.snapping  = EdgeSnapping(self, EDGE_SNAPPING_RADIUS)
        self.edgeIntersect = EdgeIntersect(self)

        # The cutline instancing
        self.cutline     = GraphicsCutLine()
        self.grScene.addItem(self.cutline)


        # general view settings
        # the zoom settings
        self.zoomInScale = 1.150
        self.zoomClamp   = True
        self.zoom        = 20.0
        self.zoomStep    = 1.0
        self.zoomRange   = [0.0, 40.0]


        self._drap_enter_listeners = []
        self._drop_listeners = []
        #self.setContextMenuPolicy(Qt.NoContextMenu)
        
        self._mouse_position = None

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


    def isSnappingEnabled(self, event: 'QInputEvent' = None) -> bool:
        """ Return ''True'' is the snapping is currently enabled"""
        return EDGE_SNAPPING if event else True

    def dragEnterEvent(self, event):
        for callback in self._drap_enter_listeners : callback(event)

    def dropEvent(self, event):
        for callback in self._drop_listeners : callback(event)

    def addDragEnterListener(self, callback):
        self._drap_enter_listeners.append(callback)

    def addDropListener(self, callback):
        self._drop_listeners.append(callback)


    def resetMode(self):
        """Helper function to re-set the grView state machine to default value"""
        self.mode = MODE_NONE


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


    def cutInersectingEdges(self):
        for ix in range(len(self.cutline.points) - 1):
            p1 = self.cutline.points[ix]
            p2 = self.cutline.points[ix + 1]

            for edge in self.grScene.scene.edges:
                if DEBUG : print("CUTTING: between points" + str(p1.x()) + str(p1.y()) +  " " + str(p2.x()) + str(p2.y()) + "  the edge is ", edge, "   grEdge is ", edge.grEdge)
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()
        if DEBUG : print("CUTTING: done")

        self.grScene.scene.history.storeHistory("cut edges")
        if DEBUG : print("CUTTING: added history stamp")

    def setSocketHighlights(self, scenepos: QPointF, highlighted: bool = True, radius: float = 50):
        """Set/disable socket highlights in Scene area defined by `scenepos` and `radius`"""
        scanrect = QRectF(scenepos.x() - radius, scenepos.y() - radius, radius * 2, radius * 2)
        items = self.grScene.items(scanrect)
        items = list(filter(lambda x: isinstance(x, GraphicsSocket), items))
        for grSocket in items: grSocket.isHighlighted = highlighted
        return items



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

        if hasattr(item, "node"):
            if self.mode == MODE_NONE:
                self.mode = MODE_NODE_DRAG
                self.edgeIntersect.enterState(item.node)


        # if the socket is within the snapping distance
        if self.isSnappingEnabled(event):
            item = self.snapping.getSnappedSocketItem(event)


        if isinstance(item, GraphicsSocket):
            if self.mode == MODE_NONE and event.modifiers() & Qt.ControlModifier:
                socket = item.socket
                if socket.hasEdges():
                    self.mode = MODE_EDGE_REROUT
                    self.rerouting.startRerouting(socket)
                    return

            if self.mode == MODE_NONE:
                self.mode = MODE_EDGE_DRAG
                self.dragging.edgeDragStart(item)
                return


        if self.mode == MODE_EDGE_DRAG:
            res = self.dragging.edgeDragEnd(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRect = True


        super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):
        # get item which we release mouse button on
        item = self.getItemAtClick(event)

        try:
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
                    
                    # defines if the snapping is enabled and returs the closest
                    # socket item
                    if self.isSnappingEnabled(event):
                        item = self.snapping.getSnappedSocketItem(event)

                    res = self.dragging.edgeDragEnd(item)
                    if res: return


            if self.mode == MODE_EDGE_REROUT:
                # defines if the snapping is enabled and returs the closest
                # socket item
                if self.isSnappingEnabled(event):
                    item = self.snapping.getSnappedSocketItem(event)

                self.rerouting.stopRerouting(item.socket if isinstance(item, GraphicsSocket) else None)
                self.mode = MODE_NONE
                return


            if self.mode == MODE_EDGE_CUT:
                try:
                    self.cutInersectingEdges()
                    self.cutline.points = []
                    self.cutline.update()
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
                except Exception as e : dumpException(e)
                self.mode = MODE_NONE
                return
            

            if self.mode == MODE_NODE_DRAG:
                scenepos = self.mapToScene(event.pos())
                self.edgeIntersect.leaveState(scenepos.x(), scenepos.y())
                self.mode = MODE_NONE
                self.update()


            if self.rubberBandDraggingRect:
                self.rubberBandDraggingRect = False
                current_selected_items = self.grScene.selectedItems()

                if current_selected_items != self.grScene.scene._last_selected_items:
                    if current_selected_items == []:
                        self.grScene.itemsDeselected.emit()
                    else:
                        self.grScene.itemSelected.emit()
                    self.grScene.scene._last_selected_items = current_selected_items

                # the rubber band rectangle doesn't disappear without handling the event
                super().mouseReleaseEvent(event)
                return

        except Exception as e: dumpException(e)

        super().mouseReleaseEvent(event)



    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)

        if DEBUG:
            if isinstance(item, GraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets:',
                                            item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is GraphicsSocket: 
                print('RMB DEBUG:', item.socket)
                if item.socket.hasEdges(): 
                    print('has edge:', item.socket.edge)

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)


    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        self._mouse_position = event.pos()
        try:
            modified = self.setSocketHighlights(pos, highlighted=False, radius=EDGE_SNAPPING_RADIUS+50)

            # defines if the snapping is enabled and returs the closest
            # socket item
            if self.isSnappingEnabled(event):
               _, pos = self.snapping.getSnappedSocketPosition(pos)

            if modified:
                self.update()

            if self.mode == MODE_EDGE_DRAG:
                if DEBUG : print("MOUS_MV: EDGE DRAG MODE")
                self.dragging.updateDestination(pos.x(), pos.y())

            if self.mode == MODE_NODE_DRAG:
                self.edgeIntersect.update(pos.x(), pos.y())

            if self.mode == MODE_EDGE_REROUT:
                self.rerouting.updateScenePos(pos.x(), pos.y())


            if self.mode == MODE_EDGE_CUT:
                if DEBUG : print("MOUS_MV: EDGE CUT MODE")
                self.cutline.points.append(pos)
                self.cutline.update()

        except Exception as e: 
            dumpException(e)

        self.last_scene_mouse_position = self.mapToScene(event.pos())
        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()),
            int(self.last_scene_mouse_position.y()))

        return super().mouseMoveEvent(event)


    def keyPressEvent(self, event):
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


    def centerContent(self):
        count = 0

        # Get bounding rect of all selected Items
        for item in self.grScene.selectedItems():
            if count == 0:
                rect = item.mapRectToScene(item.boundingRect())
            else:
                rect = rect.united(item.mapRectToScene(item.boundingRect()))
            count += 1
        if count == 0:
            self.fitInView(self.grScene.itemsBoundingRect(), Qt.KeepAspectRatio)
            self.zoom = 20
        else:
            self.fitInView(rect, Qt.KeepAspectRatio)
            self.zoom = 20
        