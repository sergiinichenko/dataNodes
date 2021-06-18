
from graphics.graphics_node import GraphicsNode
from core.node_content_widget import NodeWidget
from core.node_socket import LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP, Socket
from core.node_serializer import Serializer
from collections import OrderedDict

SOCKET_INPUT  = 1
SOCKET_OUTPUT = 2

DEBUG = False

class Node(Serializer):
    def __init__(self, scene, title="Empty node", 
                 inputs=[], outputs=[]):
        super().__init__()

        self.scene = scene
        self.title = title

        self.socket_spacing = 24.0

        self.content = NodeWidget()
        self.grNode  = GraphicsNode(self)

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        # create sockets for input and outputs
        self.inputs  = []
        self.outputs = []
        for i, item in zip(range(len(inputs)), inputs):
            self.inputs.append(Socket(node=self, inout=SOCKET_INPUT, index=i, position=LEFT_BOTTOM, soket_type=item))

        for i, item in zip(range(len(outputs)), outputs):
            self.outputs.append(Socket(node=self, inout=SOCKET_OUTPUT, index=i, position=RIGHT_TOP, soket_type=item))        

    def __str__(self) -> str:
        return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])

    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPos(self, index, position):
        x = 0.0  if position in (LEFT_TOP, LEFT_BOTTOM)  else  self.grNode.width
    
        if position in (LEFT_TOP, RIGHT_TOP):
            y = self.grNode.title_height + self.grNode._padding + self.grNode.border_radius + index * self.socket_spacing
        else:
            y = self.grNode.height - self.grNode._padding - self.grNode.border_radius - index * self.socket_spacing
        return x, y

    def remove(self):
        if DEBUG : print("> Removing the node", self)
        if DEBUG : print("  -- removing all edges from sockets")
        for socket in (self.inputs + self.outputs):
            if socket.hasEdge():
                if DEBUG : print("    - removing edge:", socket.edge, " from socket:", socket)
                socket.edge.remove()
        if DEBUG : print("  - removing the grNode ")        
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG : print("  - removing the node from the scene ")        
        self.scene.removeNode(self)
        if DEBUG : print("  - removing is done")        


    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs:  inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())

        return OrderedDict([
            ('id'      , self.id),
            ("title"   , self.title),
            ("pos_x"   , self.grNode.scenePos().x()),
            ("pos_y"   , self.grNode.scenePos().y()),
            ("inputs"  , inputs),
            ("outputs" , outputs),
            ("content" , self.content.serialize()),
        ])

        
    def deserialize(self, data, hashmap=[]):
        print("Deserialization of the data", data)
        return False