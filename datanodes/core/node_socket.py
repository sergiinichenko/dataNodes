from PyQt5.QtWidgets import *
from datanodes.graphics.graphics_socket import GraphicsSocket
from datanodes.core.node_serializer import Serializer
from collections import OrderedDict
from datanodes.core.node_settings import *


class Socket(Serializer):
    def __init__(self, node, inout, index=0, position=LEFT_TOP, soket_type=SOCKET_DATA_NUMERIC, label=None):
        super().__init__()

        self.node        = node
        self.index       = index
        self.position    = position
        self.socket_type = soket_type
        self.inout       = inout

        self.grSocket    = GraphicsSocket(self, self.socket_type, label)

        #self.grSocket.setPos(*self.node.getSocketPos(self.index, self.position))
        self.setPos()

        self.edges = []

        self._value = ""
        self._type  = ""

    def __str__(self) -> str:
        return "<Socket %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @type.setter
    def type(self, new_type):
        self._type = new_type

    @property
    def pos(self):
        return self.node.grNode.pos() +  self.grSocket.pos()

    def setPos(self):
        self.grSocket.setPos(*self.node.getSocketPos(self.index, self.position, self.inout))

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
            ('label'       , self.grSocket.label) 
        ])


    def deserialize(self, data, hashmap=[], restore_id=True):

        if restore_id : self.id = data['id']
        
        hashmap[data['id']] = self

        #self.grSocket.setPos(data['x'], data['y'])
        return True