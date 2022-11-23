from datanodes.core.node_settings import SOCKET_OUTPUT, SOCKET_INPUT
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRect, QRectF, Qt
from PyQt5.QtGui import QColor, QPen, QBrush

class GraphicsSocket(QGraphicsItem):
    def __init__(self, socket, socket_type=1, label=None):
        super().__init__(socket.node.grNode)
        self.socket_type = socket_type
        self.socket = socket

        # geometry settings of the socket
        self.radius = 7.0
        self.outline_width = 1.0

        self.initAssets()
        
        if label: self._label  = str(label)
        else:     self._label  = None

        self.isHighlighted = False

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, new_label):
        self._label = new_label

    def initAssets(self):
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
        self._color_highlight = QColor("#FF37A6FF")

        self._pen   = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        
        self._pen_white = QPen(Qt.white)
        self._pen_white.setWidthF(self.outline_width)

        self._pen_highlight = QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.0)
        
        self._brush = QBrush(self._color_background)

    def paint(self, painter, QStyleOptionGraphicsItem, widget = None):

        # pain the circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.isHighlighted else self._pen_highlight)

        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

        if self.label and self.socket.inout == SOCKET_OUTPUT:
            painter.setPen(self._pen_white)
            rect = QRect( - self.radius - 110, -10, 100, 24)
            painter.drawText(rect, Qt.AlignRight, self.label)

        if self.label and self.socket.inout == SOCKET_INPUT:
            painter.setPen(self._pen_white)
            rect = QRect( + self.radius + 10, -10, 100, 24)
            painter.drawText(rect, Qt.AlignLeft, self.label)

    def boundingRect(self):
        return QRectF(- self.radius - self.outline_width, 
                      - self.radius - self.outline_width,
                      2 * (self.radius + self.outline_width),
                      2 * (self.radius + self.outline_width)
                ).normalized()

