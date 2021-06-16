from graphics.graphics_edge import *

EDGE_DIRECT = 1
EDGE_BEZIER = 2

class Edge:
    def __init__(self, scene, start_socket, end_socket, type=EDGE_DIRECT):
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket   = end_socket

        self.grEdge = GraphicsEdgeDirect(self) if type == EDGE_DIRECT else  GraphicsEdgeBezier(self)

        self.scene.grScene.addItem(self.grEdge)

    def updatePos(self):
        self.grEdge.setSource()

    def removeFromSockets(self):
        if self.start_socket is not None:
            self.start_socket.edge = None

        if self.end_socket is not None:
            self.end_socket.edge = None

        self.start_socket = None
        self.end_socket   = None

    def remove(self):
        self.removeFromSockets()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        self.scene.removeEdge(self)

