from datanodes.graphics.graphics_edge import *
from datanodes.core.node_serializer import Serializer
from collections import OrderedDict

DEBUG = False

EDGE_DIRECT = 1
EDGE_BEZIER = 2

class Edge(Serializer):
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_BEZIER):
        super().__init__()

        # default initialization
        self._start_socket = None
        self._end_socket   = None

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket   = end_socket
        self.edge_type    = edge_type

        self.scene.addEdge(self)

    def __str__(self) -> str:
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])

    @property
    def start_socket(self): return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # if the edge was assigned to some other socket
        # then it has to be 
        if self._start_socket is not None:
            self._start_socket.disconnectEdge(self)

        # assign new start socket 
        self._start_socket = value

        # add edge to socket 
        if self.start_socket is not None:
            self.start_socket.connectEdge(self)

    @property
    def end_socket(self): return self._end_socket


    @end_socket.setter
    def end_socket(self, value):
        # if the edge was assigned to some other socket
        # then it has to be 
        if self._end_socket is not None:
            self._end_socket.disconnectEdge(self)

        # assign new end socket 
        self._end_socket = value

        # add edge to socket 
        if self.end_socket is not None:
            self.end_socket.connectEdge(self)

    @property
    def edge_type(self): return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)

        self._edge_type = value
        if self._edge_type == EDGE_DIRECT:
            self.grEdge = GraphicsEdgeDirect(self)
        
        elif self._edge_type == EDGE_BEZIER:
            self.grEdge = GraphicsEdgeBezier(self)
        
        else:
            self.grEdge = GraphicsEdgeBezier(self)
        self.scene.grScene.addItem(self.grEdge)

    def updatePos(self):
        self.grEdge.setSource()

    def removeFromSockets(self):
        """
        if self.start_socket is not None:
            self.start_socket.disconnectEdge(self)

        if self.end_socket is not None:
            self.end_socket.disconnectEdge(self)
        """
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

    def deserialize(self, data, hashmap=[], restore_id=True):

        if restore_id : self.id = data['id']

        self.start_socket = hashmap[data['start']]
        self.end_socket   = hashmap[data['end']]
        self.edge_type    = data['edge_type']

        return True
