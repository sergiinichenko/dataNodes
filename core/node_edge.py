from graphics.graphics_edge import *
from core.node_serializer import Serializer
from collections import OrderedDict

DEBUG = False

EDGE_DIRECT = 1
EDGE_BEZIER = 2

class Edge(Serializer):
    def __init__(self, scene, start_socket, end_socket, edge_type=EDGE_BEZIER):
        super().__init__()

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket   = end_socket

        self.edge_type = edge_type

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
        if DEBUG : print("> Removing edge:", self)
        if DEBUG : print("  - removing edge from all sockets")
        self.removeFromSockets()

        if DEBUG : print("  - removing edge from scene")
        self.scene.grScene.removeItem(self.grEdge)

        if DEBUG : print("  - grNode to None")
        self.grEdge = None

        if DEBUG : print("  - removing the edge")
        try: self.scene.removeEdge(self)
        except Exception as e: pass

        self = None
        if DEBUG : print("  - edge remove is done")


    def serialize(self):
        return OrderedDict([
            ('id'        , self.id),
            ('edge_type' , self.edge_type),
            ('start'     , self.start_socket.id),
            ('end'       , self.end_socket.id),
        ])

    def deserialize(self, data, hashmap=[]):
        print("Deserialization of the data", data)
        return False
