from datanodes.core.node_socket import LEFT_BOTTOM, RIGHT_BOTTOM, RIGHT_TOP, LEFT_TOP
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *

class GraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge      = edge

        self._widht    = 3.0
        self._color    = QColor("#001000")
        self._selected = QColor("#00ff00")

        self._pen      = QPen(self._color)
        self._pen_sel  = QPen(self._selected)
        self._pen_drag = QPen(self._color)
        self._pen.setWidth(self._widht)
        self._pen_sel.setWidth(self._widht)
        self._pen_drag.setWidth(self._widht)
        self._pen_drag.setStyle(Qt.DashLine)

        self.setZValue(-2.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        if self.edge.start_socket is not None:
            self.destination = QPoint(self.edge.start_socket.pos.x(), self.edge.start_socket.pos.y())
        else:
            self.destination = QPoint(0.0, 0.0)



    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcPath())

        if self.edge.end_socket == None:
            painter.setPen(self._pen_drag)
        else:            
            painter.setPen(self._pen if not self.isSelected() else self._pen_sel)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def calcPath(self):
        """ Handles drawing  """
        raise NotImplemented("This method has to be overwritten in a child class")
    
    def getSourcePos(self):
        if self.edge.start_socket is not None:
            return self.edge.start_socket.pos
        else:
            return QPointF(0,0)

    def getDestinationPos(self):
        if self.edge.end_socket is not None:
            return self.edge.end_socket.pos
        else:
            return self.destination

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

class GraphicsEdgeDirect(GraphicsEdge):
    def calcPath(self):
        fr = self.getSourcePos()
        to = self.getDestinationPos()

        path = QPainterPath(QPoint(fr.x(), fr.y()))
        path.lineTo(QPoint(to.x(), to.y()))
        return path

class GraphicsEdgeBezier(GraphicsEdge):
    def calcPath(self):
        fr = self.getSourcePos()
        to = self.getDestinationPos()
        dist = (to.x() - fr.x())*0.5

        cpx_fr = +100
        cpx_to = -100
        cpy_fr = 0
        cpy_to = 0

        #if self.edge.start_socket is not None:
        spos = self.edge.start_socket.position

        if spos in(LEFT_BOTTOM, LEFT_TOP):
            cpx_fr *= -1
            cpx_to *= -1

        path = QPainterPath(QPoint(fr.x(), fr.y()))
        path.cubicTo(fr.x() + cpx_fr, fr.y() + cpy_fr, 
                     to.x() + cpx_to, to.y() + cpy_to, 
                     to.x(), to.y())

        return path

