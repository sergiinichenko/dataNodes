
from graphics.graphics_node import GraphicsNode
from core.node_content_widget import NodeWidget
from core.node_socket import LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP, Socket

class Node:
    def __init__(self, scene, title="Empty node", 
                 inputs=[], outputs=[]):
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
            self.inputs.append(Socket(node=self, index=i, position=LEFT_BOTTOM))

        for i, item in zip(range(len(outputs)), outputs):
            self.outputs.append(Socket(node=self, index=i, position=RIGHT_TOP))        

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
