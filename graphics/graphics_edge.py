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
        self.destination = QPoint(self.edge.start_socket.pos.x(), self.edge.start_socket.pos.y())

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.updatePath()

        if self.edge.end_socket == None:
            painter.setPen(self._pen_drag)
        else:            
            painter.setPen(self._pen if not self.isSelected() else self._pen_sel)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def updatePath(self):
        """ Handles drawing  """
        raise NotImplemented("This method has to be overwritten in a child class")
    
    def getSourcePos(self):
        return self.edge.start_socket.pos

    def getDestinationPos(self):
        if self.edge.end_socket is not None:
            return self.edge.end_socket.pos
        else:
            return self.destination



class GraphicsEdgeDirect(GraphicsEdge):
    def updatePath(self):
        fr = self.getSourcePos()
        to = self.getDestinationPos()

        path = QPainterPath(QPoint(fr.x(), fr.y()))
        path.lineTo(QPoint(to.x(), to.y()))
        self.setPath(path)

class GraphicsEdgeBezier(GraphicsEdge):
    def updatePath(self):
        fr = self.getSourcePos()
        to = self.getDestinationPos()
        
        dist = (to.x() - fr.x())*0.5
        if fr.x() > to.x() : dist *= -1

        path = QPainterPath(QPoint(fr.x(), fr.y()))
        path.cubicTo(fr.x() + dist, fr.y(), to.x() - dist, to.y(), to.x(), to.y())
        self.setPath(path)

