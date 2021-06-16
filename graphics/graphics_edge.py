from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *

class GraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge      = edge
        self._color    = QColor("#001000")
        self._selected = QColor("#00ff00")
        self._pen      = QPen(self._color)
        self._pen_sel  = QPen(self._selected)
        self._pen.setWidth(2.0)
        self._pen_sel.setWidth(2.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.updatePath()
        painter.setPen(self._pen if not self.isSelected() else self._pen_sel)

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def updatePath(self):
        """ Handles drawing  """
        raise NotImplemented("This method has to be overwritten in a child class")
    


class GraphicsEdgeDirect(GraphicsEdge):
    def updatePath(self):
        fr = self.edge.start_socket.pos
        to = self.edge.end_socket.pos

        print(fr[0], fr[1])
        print(to[0], to[1])
        path = QPainterPath(QPoint(fr[0], fr[1]))
        path.lineTo(QPoint(to[0], to[1]))

class GraphicsEdgeBezier(GraphicsEdge):
    def updatePath(self):
        path = QPainterPath(QPoint(self.edge.start_socket.grSocket.pos().x(), self.edge.start_socket.grSocket.pos().y()))
        path.lineTo(QPoint(self.edge.end_socket.grSocket.pos().x(), self.edge.end_socket.grSocket.pos().y()))

