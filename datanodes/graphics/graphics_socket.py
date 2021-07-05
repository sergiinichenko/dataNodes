from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GraphicsSocket(QGraphicsItem):
    def __init__(self, socket, socket_type=1, label=None):
        super().__init__(socket.node.grNode)
        self.socket_type = socket_type
        self.socket = socket

        # geometry settings of the socket
        self.node = socket.node.grNode
        self.radius = 7.0
        self.outline_width = 1.0
        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFb54747"),
            QColor("#FFdbe220")
        ]
        self._color_background = self._colors[self.socket_type]
        self._color_outline    = QColor("#FF000000")

        self._pen   = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        
        self._pen_white = QPen(Qt.white)
        self._pen_white.setWidthF(self.outline_width)

        self._brush = QBrush(self._color_background)
        if label: self.label  = str(label)
        else:     self.label  = None

    def paint(self, painter, QStyleOptionGraphicsItem, widget = None):

        # pain the circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

        if self.label:
            painter.setPen(self._pen_white)
            rect = QRect( - self.radius - 105, -10, 100, 24)
            painter.drawText(rect, Qt.AlignRight, self.label)

    def boundingRect(self):
        return QRectF(- self.radius - self.outline_width, 
                      - self.radius - self.outline_width,
                      2 * (self.radius + self.outline_width),
                      2 * (self.radius + self.outline_width)
                ).normalized()

