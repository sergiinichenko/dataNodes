from datanodes.graphics.graphics_socket import GraphicsSocket
from datanodes.core.node_serializer import Serializer
from collections import OrderedDict

LEFT_TOP     = 1
LEFT_BOTTOM  = 2
RIGHT_TOP    = 3
RIGHT_BOTTOM = 4

class Socket(Serializer):
    def __init__(self, node, inout, index=0, position=LEFT_TOP, soket_type=1):
        super().__init__()

        self.node   = node
        self.index  = index
        self.position = position
        self.socket_type = soket_type
        self.inout  = inout

        self.grSocket = GraphicsSocket(self, self.socket_type)

        self.grSocket.setPos(*self.node.getSocketPos(self.index, self.position))

        self.edges = []

    def __str__(self) -> str:
        return "<Socket %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])


    @property
    def pos(self):
        return self.node.grNode.pos() +  self.grSocket.pos()

    def connectEdge(self, edge):
        self.edges.append(edge)

    def disconnectEdge(self, edge):
        if self.hasEdgeIn(edge):
            self.edges.remove(edge)
        else:
            print("!W:", "Socket::disconnectEdge", "Edge is not in the list")

    def clearEdges(self):
        if self.hasEdge():
            for edge in self.edges:
                edge.remove()
            self.edges = []

    def hasEdgeIn(self, edge):
        return edge in self.edges

    def hasEdge(self):
        return len(self.edges) > 0


    def serialize(self):
        return OrderedDict([
            ('id'          , self.id),
            ('index'       , self.index),
            ('position'    , self.position),
            ('socket_type' , self.socket_type),
            ('inout'       , self.inout),
            ('x'           , self.grSocket.pos().x()),
            ('y'           , self.grSocket.pos().y()),
        ])


    def deserialize(self, data, hashmap=[], restore_id=True):

        if restore_id : self.id = data['id']
        
        hashmap[data['id']] = self

        self.grSocket.setPos(data['x'], data['y'])
        return True