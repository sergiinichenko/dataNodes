from datanodes.graphics.graphics_socket import GraphicsSocket
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QPointF, QRectF
from datanodes.core.node_socket import Socket

DEBUG_SNAPPING = True

class EdgeSnapping:
    def __init__(self, grView:'QGraphicsView', snapping_radius:float = 20):
        self.grView          = grView
        self.grScene         = self.grView.grScene
        self.snapping_radius = snapping_radius


    def getSnappedSocketItem(self, event:'QMouseEvent'):
        scenepos = self.grView.mapToScene(event.pos())
        grSocket, pos = self.getSnappedSocketPosition(scenepos)
        return grSocket

    def getSnappedSocketPosition(self, scenepos:'QPointF'):
        """
        Returns grSocket and Scene position to nearest Socket or original position if no nearby Socket found

        :param scenepos: From which point should I snap?
        :type scenepos: ``QPointF``
        :return: grSocket and Scene postion to nearest socket
        """
        scanrect = QRectF(
            scenepos.x() - self.snapping_radius, scenepos.y() - self.snapping_radius,
            self.snapping_radius * 2, self.snapping_radius * 2
        )
        items = self.grScene.items(scanrect)
        items = list(filter(lambda x: isinstance(x, GraphicsSocket), items))

        if len(items) == 0:
            return None, scenepos

        selected_item = items[0]
        if len(items) > 1:
            # calculate the nearest socket
            nearest = 10000000000
            for grsock in items:
                grsock_scenepos = grsock.socket.node.getSocketScenePosition(grsock.socket)
                qpdist = QPointF(*grsock_scenepos) - scenepos
                dist = qpdist.x() * qpdist.x() + qpdist.y() * qpdist.y()
                if dist < nearest:
                    nearest, selected_item = dist, grsock

        selected_item.isHighlighted = True

        calcpos = selected_item.socket.node.getSocketScenePosition(selected_item.socket)

        return selected_item, QPointF(*calcpos)