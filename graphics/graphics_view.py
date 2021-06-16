from typing import FrozenSet
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent = None):
        super().__init__(parent)

        self.grScene = scene.grScene

        self.initUI()

        self.setScene(self.grScene)

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

    # Remap the mouse press events to custom functions
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
        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)


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

