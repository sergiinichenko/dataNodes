
from datanodes.core.utils import dumpException
from PyQt5.sip import dump
from datanodes.graphics.graphics_group import GraphicsGroup
from datanodes.core.node_content_widget import NodeContentWidget
from datanodes.core.node_socket import LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP, Socket
from datanodes.core.node_serializer import Serializer
from collections import OrderedDict
from datanodes.core.node_settings import *


DEBUG = False

class Group(Serializer):
    """
    Class representing `Group` in the `Scene`.
    """
    GraphicsNode_class = GraphicsGroup
    NodeContent_class = NodeContentWidget
    Socket_class = Socket

    def __init__(self, scene, title="Empty node", 
                 inputs=[], outputs=[], innames=None, outnames=None):
        super().__init__()
        self._title = title
        self.scene  = scene

        self.initInnerClasses()
        self.initSettings()

        self.title  = self._title

        # just to be sure, init these variables
        self.content = NodeContentWidget
        self.grNode  = GraphicsGroup

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        # create sockets from inner nodes input and outputs
        self.inputs  = []
        self.outputs = []
        self.recalculate = False

        # node state flags
        self._is_dirty   = False
        self._is_invalid = False
        self._is_mute    = False

        self.initSockets(inputs, outputs, innames=innames, outnames=outnames)
        self.onCreate()

    def onCreate(self):
        pass

    def initInnerClasses(self):
        pass

    def initSettings(self):
        self.socket_spacing = 24.0
        self.socket_top_margin = self.grNode.title_height + self.grNode._vpadding + self.grNode.border_radius
        self.socket_bottom_margin = self.grNode.border_radius + self.grNode._vpadding
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

    def initSockets(self, inputs, outputs, reset=True, innames=None, outnames=None):
        self.in_count  = len(inputs)
        self.out_count = len(outputs)
        if reset:
            # clear the sockets
            if hasattr(self, "inputs") and hasattr(self, "outputs"):
                # remove grSockets from the scene
                self.clearInputs()
                self.clearOutputs()

        # create new sockets
        self.createInputs(inputs, innames)
        self.createOutputs(outputs, outnames)


    def clearOutputs(self):
        for socket in self.outputs:
            if socket.hasEdges():
                socket.clearEdges()
            self.scene.grScene.removeItem(socket.grSocket)
        self.outputs = []

    def clearInputs(self):
        for socket in self.inputs:
            if socket.hasEdges():
                socket.clearEdges()
            self.scene.grScene.removeItem(socket.grSocket)
        self.inputs = []

    def createInputs(self, inputs, names=None):
        for i, item in zip(range(len(inputs)), inputs):
            if names:
                self.inputs.append(Socket(node=self, inout=SOCKET_INPUT, index=i, position=self.input_socket_position, soket_type=item, label=names[i]))        
            else:
                self.inputs.append(Socket(node=self, inout=SOCKET_INPUT, index=i, position=self.input_socket_position, soket_type=item))


    def createOutputs(self, outputs, names=None):
        for i, item in zip(range(len(outputs)), outputs):
            if names:
                self.outputs.append(Socket(node=self, inout=SOCKET_OUTPUT, index=i, position=self.output_socket_position, soket_type=item, label=names[i]))        
            else:
                self.outputs.append(Socket(node=self, inout=SOCKET_OUTPUT, index=i, position=self.output_socket_position, soket_type=item))        

    @property
    def pos(self):
        return self.grNode.pos()

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title


    def onEdgeConnectionChanged(self, new_edge=None):
        pass
    

    def onInputChanged(self, new_edge=None):
        self.setDirty()
        self.setDescendentsDirty()


    def isDirty(self):
        return self._is_dirty

    def setDirty(self, value=True):
        self._is_dirty = value
        if self._is_dirty:
            self.onSetDirty()

    def setChildrenDirty(self, value=True):
        for child in self.getChildNodes():
            child.setDirty(value)

    def setDescendentsDirty(self, value=True):
        for other_node in self.getChildNodes():
            other_node.setDirty(value)
            other_node.setChildrenDirty(value)

    def onSetDirty(self):
        self.grNode.update()

    def isInvalid(self):
        return self._is_invalid

    def setInvalid(self, value=True):
        self._is_invalid = value
        if self._is_invalid:
            self.onSetInvalid()

    def onSetInvalid(self):
        self.grNode.update()

    def setChildrenInvalid(self, value=True):
        for child in self.getChildNodes():
            child.setInvalid(value)

    def setDescendentsInvalid(self, value=True):
        for other_node in self.getChildNodes():
            other_node.setInvalid(value)
            other_node.setChildrenInvalid(value)


    def isMute(self):
        return self._is_mute
    
    def setMute(self, value=True):
        self._is_mute = value
        if self._is_mute:
            self.onSetMute()
        self.setDirty()
        self.eval()
        self.evalChildren()

    def onSetMute(self):
        pass



    def hasEdge(self, edge: 'Edge'):
        """Returns ``True`` if edge is connected to any :class:`~nodeeditor.node_socket.Socket` of this `Node`"""
        for socket in (self.inputs + self.outputs):
            if socket.hasEdge(edge):
                return True
        return False


    
    # Traversing functions
    def getChildNodes(self):
        if self.outputs == [] : return []
        child_nodes = []
        for ix in range(len(self.outputs)):
            for edge in self.outputs[ix].edges:
                child_nodes.append( edge.getOtherSocket(self.outputs[ix]).node )

        return child_nodes


    def getInput(self, index=0):
        try:
            if self.inputs[index].hasEdges():
                return self.inputs[index]
            else:
                return None

        except IndexError:
            print("EXC: Trying to get input but nothing is attached")
            return None

        except Exception as e: 
            dumpException(e)
            return None


    def getInputs(self):
        inputs = []
        try:
            if len(self.inputs) == 0: return None
            return self.inputs
            
        except IndexError:
            print("EXC: Trying to get input but nothing is attached")
            return None

        except Exception as e: 
            dumpException(e)
            return None


    def getOutput(self, index=0):
        try:
            return self.outputs[index]

        except IndexError:
            print("EXC: Trying to get input but nothing is attached")
            return None

        except Exception as e: 
            dumpException(e)
            return None


    def getOutputs(self):
        try:
            if len(self.outputs) == 0: return None
            return self.outputs
            
        except IndexError:
            print("EXC: Trying to get input but nothing is attached")
            return None

        except Exception as e: 
            dumpException(e)
            return None


    def getOutputNodes(self, index: int=0):
        """
        Get **all** `Nodes` connected to the Output specified by `index`

        :param index: Order number of the `Output Socket`
        :type index: ``int``
        :return: all :class:`~nodeeditor.node_node.Node` instances which are connected to the
            specified `Output` or ``[]`` if there is no connection or the index is out of range
        :rtype: List[:class:`~nodeeditor.node_node.Node`]
        """
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    def getInputNodes(self, index: int=0):
        """
        Get the **first**  `Node` connected to the  Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: :class:`~nodeeditor.node_node.Node` which is connected to the specified `Input` or ``None`` if
            there is no connection or the index is out of range
        :rtype: :class:`~nodeeditor.node_node.Node` or ``None``
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except Exception as e:
            dumpException(e)
            return None

    def eval(self, silent=False):
        self.setDirty(False)
        self.setInvalid(False)
        return 0

    def evalChildren(self):
        for node in self.getChildNodes():
            node.eval()

    def update(self, silent=False):
        self.setDirty()
        self.setDescendentsDirty()
        self.eval()
        self.evalChildren()

    def updateDescendents(self):
        for other_node in self.getChildNodes():
            other_node.update()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPos(self, index, position, inout):
        if inout == SOCKET_INPUT  : count = self.in_count
        if inout == SOCKET_OUTPUT : count = self.out_count

        x = self.socket_offsets[position] if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.grNode.width + self.socket_offsets[position]
    
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.socket_bottom_margin - index * self.socket_spacing
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
            y = self.socket_top_margin + index * self.socket_spacing
        else:
            # this should never happen
            y = 0

        return x, y




    def getSocketScenePosition(self, socket:'Socket') -> '(x, y)':
        """
        Get absolute Socket position in the Scene

        :param socket: `Socket` which position we want to know
        :return: (x, y) Socket's scene position
        """
        nodepos   = self.grNode.pos()
        socketpos = self.getSocketPos(socket.index, socket.position, socket.inout)

        return socket.pos.x(), socket.pos.y() #(nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])


    def remove(self):
        if DEBUG : print("> Removing the node", self)
        if DEBUG : print("  -- removing all edges from sockets")
        for socket in (self.inputs + self.outputs):
            if socket.hasEdges():
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
                           soket_type=socket_data['socket_type'],
                           label = socket_data['label'] if 'label' in socket_data else None)
            soket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(soket)

        self.outputs = []
        for socket_data in data["outputs"]:
            soket = Socket(node=self, 
                           inout=socket_data['inout'], 
                           index=socket_data['index'], 
                           position=socket_data['position'], 
                           soket_type=socket_data['socket_type'],
                           label = socket_data['label'] if 'label' in socket_data else None) 
            soket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(soket)
        
        # deserialize the content of the node
        res = self.content.deserialize(data['content'], hashmap)

        return True & res