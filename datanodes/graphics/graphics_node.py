
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GraphicsNode(QGraphicsItem):
    def __init__(self, node, parent=None):
        
        super().__init__(parent)

        self.node    = node
        self.content = self.node.content

        # init the flags
        self._wasMoved = False
        self._lastSelectedState = False

        self.initSizes()
        self.initAssets()
        self.initUI()

    def initSizes(self):
        self.width  = 180.0
        self.height = 240.0
        self.border_radius = 10.0
        self.title_height = 24.0
        self._padding     = 5.0

    def initAssets(self):
        # General graphical settings
        self._title_color = Qt.white
        self._title_font  = QFont("Ubuntu", 10)
        self._pen_default  = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))



    def onSelected(self):
        self.node.scene.grScene.itemSelected.emit()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self._wasMoved = True


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._wasMoved:
            self._wasMoved = False
            self.node.scene.history.storeHistory("nodes was moved")

            self.node.scene.resetLastSelectedStates()
            self._lastSelectedState = True
            self.node.scene._last_selected_items = self.node.scene.selectedItems()
            
            return 

        if self._lastSelectedState != self.isSelected() or self.node.scene._last_selected_items != self.scene.selectedItems():
            self.node.scene.resetLastSelectedStates()
            self._lastSelectedState = self.isSelected()
            self.onSelected()


    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def initUI(self):
        self.initTile()
        self.title = self.node.title

        self.initSockets()
        self.initContent()

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)


    def boundingRect(self):
        return QRectF(0.0, 0.0,
                    self.width,
                    self.height
                ).normalized()

    def initTile(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)

    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.border_radius, self.title_height + self.border_radius, 
                                 self.width - 2 * self.border_radius, self.height - 2 * self.border_radius - self.title_height)
        self.grContent.setWidget(self.content)


    def initSockets(self):
        pass


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        
        # paint the title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0,self.width, self.title_height,
                self.border_radius, self.border_radius)
        path_title.addRect(0, self.title_height - self.border_radius, self.border_radius, self.border_radius)
        path_title.addRect(self.width - self.border_radius, self.title_height - self.border_radius, self.border_radius, self.border_radius)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # paint the content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height,
                                self.width, self.height - self.title_height,
                                self.border_radius, self.border_radius)
        path_content.addRect(0, self.title_height, self.border_radius, self.border_radius)
        path_content.addRect(self.width-self.border_radius, self.title_height, self.border_radius, self.border_radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # paint the outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0.0, 0.0, 
                self.width, self.height, 
                self.border_radius, self.border_radius)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())