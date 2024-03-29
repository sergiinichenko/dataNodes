from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import pyqtSignal, QLine
import math

class GraphicsScene(QGraphicsScene):

    itemSelected    = pyqtSignal()
    itemsDeselected = pyqtSignal()

    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        # graphics settings
        self.gridSize = 20
        self.gridSquares = 5

        self._color_background = QColor("#212121")
        self._color_light = QColor("#1E1E1E")
        self._color_dark  = QColor("#1A1A1A")

        self.pen_light = QPen(self._color_light)
        self.pen_light.setWidth(2)

        self.pen_dark = QPen(self._color_dark)
        self.pen_dark.setWidth(3)

        self.setBackgroundBrush(self._color_background)

    # The drag enter event wont be allowed unless is overwritten (disabled)
    def dragMoveEvent(self, event):
        pass

    def setGrScene(self, width, height):
        self.setSceneRect(-width//2, -height//2, width, height)


    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # draw the grid in the window
        left  = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top   = int(math.ceil(rect.top()))
        bottom= int(math.floor(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top  = top  - (top  % self.gridSize)

        # compute the lines to be drawn
        lines_light = []
        lines_dark  = []
        # compute vertical lines of the grid
        for x in range(first_left, right, self.gridSize):
            lines_light.append(QLine(x,top,x,bottom))

        # compute horizontal lines of the grid
        for x in range(first_top, bottom, self.gridSize):
            lines_light.append(QLine(left,x,right,x))

        # compute vertical lines of the grid
        for x in range(first_left, right, self.gridSize*self.gridSquares):
            lines_dark.append(QLine(x,top,x,bottom))

        # compute horizontal lines of the grid
        for x in range(first_top, bottom, self.gridSize*self.gridSquares):
            lines_dark.append(QLine(left,x,right,x))


        painter.setPen(self.pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self.pen_dark)
        painter.drawLines(*lines_dark)        