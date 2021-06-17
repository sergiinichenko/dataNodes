from graphics.graphics_edge import *

EDGE_DIRECT = 1
EDGE_BEZIER = 2

class Edge:
    def __init__(self, scene, start_socket, end_socket, edge_type=EDGE_BEZIER):
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket   = end_socket

        self.start_socket.edge = self
        if self.end_socket is not None:
            self.end_socket.edge = self

        self.grEdge = GraphicsEdgeDirect(self) if edge_type == EDGE_DIRECT else  GraphicsEdgeBezier(self)

        self.scene.grScene.addItem(self.grEdge)
        self.scene.addEdge(self)

    def __str__(self) -> str:
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])

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

