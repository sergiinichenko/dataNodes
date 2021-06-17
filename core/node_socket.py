from graphics.graphics_socket import GraphicsSocket

LEFT_TOP     = 1
LEFT_BOTTOM  = 2
RIGHT_TOP    = 3
RIGHT_BOTTOM = 4

class Socket:
    def __init__(self, node, index=0, position=LEFT_TOP, soket_type=1):

        self.node   = node
        self.index  = index
        self.position = position
        self.socket_type = soket_type

        self.grSocket = GraphicsSocket(self, self.socket_type)

        self.grSocket.setPos(*self.node.getSocketPos(self.index, self.position))

        self.edge = None

    def __str__(self) -> str:
        return "<Socket %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])


    @property
    def pos(self):
        return self.node.grNode.pos() +  self.grSocket.pos()

    def setEdge(self, edge = None):
        self.edge = edge

