
from datanodes.graphics.graphics_node import GraphicsNode
from datanodes.core.node_content_widget import NodeContentWidget
from datanodes.core.node_socket import LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP, Socket
from datanodes.core.node_serializer import Serializer
from collections import OrderedDict
from datanodes.core.node_settings import *


DEBUG = False

class Node(Serializer):
    def __init__(self, scene, title="Empty node", 
                 inputs=[], outputs=[]):
        super().__init__()
        self._title = title
        self.scene  = scene

        self.initInnerClasses()
        self.initSettings()

        self.title  = self._title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        # create sockets for input and outputs
        self.inputs  = []
        self.outputs = []
        self.initSockets(inputs, outputs)

    def initInnerClasses(self):
        self.content = NodeContentWidget(self)
        self.grNode  = GraphicsNode(self)

    def initSettings(self):
        self.socket_spacing = 24.0
        self.input_socket_position  = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.socket_offsets = {
            LEFT_BOTTOM: -1,
            LEFT_CENTER: -1,
            LEFT_TOP:    -1,
            RIGHT_BOTTOM: 1,
            RIGHT_CENTER: 1,
            RIGHT_TOP:    1,
        }

    def initSockets(self, inputs, outputs, reset=True):
        self.in_count  = len(inputs)
        self.out_count = len(outputs)
        if reset:
            # clear the sockets
            if hasattr(self, "inputs") and hasattr(self, "outputs"):
                # remove grSockets from the scene
                for socket in (self.inputs + self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs  = []
                self.outputs = []

        # create new sockets
        for i, item in zip(range(len(inputs)), inputs):
            self.inputs.append(Socket(node=self, inout=SOCKET_INPUT, index=i, position=self.input_socket_position, soket_type=item))

        for i, item in zip(range(len(outputs)), outputs):
            self.outputs.append(Socket(node=self, inout=SOCKET_OUTPUT, index=i, position=self.output_socket_position, soket_type=item))        


    def __str__(self) -> str:
        return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])

    @property
    def pos(self):
        return self.grNode.pos()

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title


    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPos(self, index, position, inout):
        if inout == SOCKET_INPUT  : count = self.in_count
        if inout == SOCKET_OUTPUT : count = self.out_count

        x = self.socket_offsets[position] if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.grNode.width + self.socket_offsets[position]
    
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.border_radius - self.grNode._vpadding - index * self.socket_spacing
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = count
            node_height = self.grNode.height
            top_offset = self.grNode.title_height + 2 * self.grNode._vpadding + self.grNode.border_radius
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_sockets * self.socket_spacing
            new_top = available_height - total_height_of_all_sockets

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height/2.0 + (index-0.5)*self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets-1)/2

        elif position in (LEFT_TOP, RIGHT_TOP):
            # start from top
            y = self.grNode.title_height + self.grNode._vpadding + self.grNode.border_radius + index * self.socket_spacing
        else:
            # this should never happen
            y = 0

        return x, y

    def remove(self):
        if DEBUG : print("> Removing the node", self)
        if DEBUG : print("  -- removing all edges from sockets")
        for socket in (self.inputs + self.outputs):
            if socket.hasEdge():
                if DEBUG : print("    - removing edge:", socket.edges, " from socket:", socket)
                socket.clearEdges()
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
        ser_content = self.content.serialize() if isinstance(self.content, Serializer) else {}

        return OrderedDict([
            ('id'      , self.id),
            ("title"   , self.title),
            ("pos_x"   , self.grNode.scenePos().x()),
            ("pos_y"   , self.grNode.scenePos().y()),
            ("inputs"  , inputs),
            ("outputs" , outputs),
            ("content" , ser_content),
        ])

    def deserialize(self, data, hashmap=[], restore_id=True):

        if restore_id : self.id = data['id']
        hashmap[data['id']] = self

        self.title = data['title']
        self.setPos(data['pos_x'], data['pos_y'])

        self.inputs = []
        for socket_data in data["inputs"]:
            soket = Socket(node=self, 
                           inout=socket_data['inout'], 
                           index=socket_data['index'], 
                           position=socket_data['position'], 
                           soket_type=socket_data['socket_type'])
            soket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(soket)

        self.outputs = []
        for socket_data in data["outputs"]:
            soket = Socket(node=self, 
                           inout=socket_data['inout'], 
                           index=socket_data['index'], 
                           position=socket_data['position'], 
                           soket_type=socket_data['socket_type'])
            soket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(soket)
        
        # deserialize the content of the node
        res = self.content.deserialize(data['content'], hashmap)

        return True & res