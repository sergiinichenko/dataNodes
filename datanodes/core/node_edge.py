from datanodes.core.utils import dumpException
from datanodes.core.node_settings import SOCKET_INPUT, SOCKET_OUTPUT
from datanodes.graphics.graphics_edge import *
from datanodes.core.node_serializer import Serializer
from collections import OrderedDict

DEBUG = False

EDGE_DIRECT = 1
EDGE_BEZIER = 2

class Edge(Serializer):
    """
    Class for representing Edge in DataNodes.
    """

    edge_validators = []        #: class variable containing list of registered edge validators

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

    def notifyOnConnection(self):
        for socket in [self.start_socket, self.end_socket]:
            socket.node.onEdgeConnectionChanged(self)
            if socket.is_input:  socket.node.onInputChanged(socket)
            if socket.is_output: socket.node.onOutputChanged(socket)

    def __str__(self) -> str:
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-4:])

    def getOtherSocket(self, the_soket):
        return self.start_socket if the_soket == self.end_socket else self.end_socket

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
        self.grEdge = self.createEdgeClassInstance(self.edge_type)
        self.scene.grScene.addItem(self.grEdge)


    @classmethod
    def getEdgeValidators(cls):
        """Return the list of Edge Validator Callbacks"""
        return cls.edge_validators

    @classmethod
    def registerEdgeValidator(cls, validator_callback: 'function'):
        """Register Edge Validator Callback

        :param validator_callback: A function handle to validate Edge
        :type validator_callback: `function`
        """
        cls.edge_validators.append(validator_callback)

    @classmethod
    def validateEdge(cls, start_socket: 'Socket', end_socket: 'Socket') -> bool:
        """Validate Edge agains all registered `Edge Validator Callbacks`

        :param start_socket: Starting :class:`~nodeeditor.node_socket.Socket` of Edge to check
        :type start_socket: :class:`~nodeeditor.node_socket.Socket`
        :param end_socket: Target/End :class:`~nodeeditor.node_socket.Socket` of Edge to check
        :type end_socket: :class:`~nodeeditor.node_socket.Socket`
        :return: ``True`` if the Edge is valid or ``False`` if not
        :rtype: ``bool``
        """
        for validator in cls.getEdgeValidators():
            if not validator(start_socket, end_socket):
                return False
        return True





    def determiteEdgeClass(self, edge_type:int):
        if edge_type == EDGE_DIRECT:
            return GraphicsEdgeDirect
        else:
            return GraphicsEdgeBezier


    def createEdgeClassInstance(self, edge_type:int):
        edgeClass = self.determiteEdgeClass(edge_type)
        edge = edgeClass(self)
        return edge

    """
    @property
    def value(self):
        if self.start_socket.inout == SOCKET_OUTPUT:
            return self.start_socket.value
        else:
            return self.end_socket.value

    @value.setter
    def value(self, new_value):
        if self.start_socket.inout == SOCKET_OUTPUT:
            self.start_socket.value = new_value
        else:
            self.end_socket.value = new_value

    @property
    def type(self):
        if self.start_socket.inout == SOCKET_OUTPUT:
            return self.start_socket.type
        else:
            return self.end_socket.type
    """


    def updatePos(self):
        source_pos = self.start_socket.pos
        source_pos = source_pos + self.start_socket.node.grNode.pos()
        self.grEdge.setSource(source_pos.x(), source_pos.y())
        if self.end_socket is not None:
            end_pos = self.end_socket.pos
            end_pos = end_pos + self.end_socket.node.grNode.pos()
            self.grEdge.setDestination(end_pos.x(), end_pos.y())
        else:
            self.grEdge.setDestination(source_pos.x(), source_pos.y())
        self.grEdge.update()



    def removeFromSockets(self):
        """
        if self.start_socket is not None:
            self.start_socket.disconnectEdge(self)

        if self.end_socket is not None:
            self.end_socket.disconnectEdge(self)
        """
        self.start_socket = None
        self.end_socket   = None

    def remove(self, silent_for_socket:'Socket'=None, silent=False):
        """
        Safely remove this Edge.

        Removes `Graphics Edge` from the ``QGraphicsScene`` and it's reference to all GC to clean it up.
        Notifies nodes previously connected :class:`~nodeeditor.node_node.Node` (s) about this event.

        Triggers Nodes':

        - :py:meth:`~nodeeditor.node_node.Node.onEdgeConnectionChanged`
        - :py:meth:`~nodeeditor.node_node.Node.onInputChanged`

        :param silent_for_socket: :class:`~nodeeditor.node_socket.Socket` of a :class:`~nodeeditor.node_node.Node` which
            won't be notified, when this ``Edge`` is going to be removed
        :type silent_for_socket: :class:`~nodeeditor.node_socket.Socket`
        :param silent: ``True`` if no events should be triggered during removing
        :type silent: ``bool``
        """
        old_sockets = [self.start_socket, self.end_socket]

        # ugly hack, since I noticed that even when you remove grEdge from scene,
        # sometimes it stays there! How dare you Qt!
        if DEBUG: print(" - hide grEdge")
        self.grEdge.hide()

        if DEBUG: print(" - remove grEdge", self.grEdge)
        self.scene.grScene.removeItem(self.grEdge)
        if DEBUG: print("   grEdge:", self.grEdge)

        self.scene.grScene.update()

        if DEBUG: print("# Removing Edge", self)
        if DEBUG: print(" - remove edge from all sockets")
        self.removeFromSockets()
        if DEBUG: print(" - remove edge from scene")
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        if DEBUG: print(" - everything is done.")

        try:
            # notify nodes from old sockets
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        # if we requested silence for Socket and it's this one, skip notifications
                        continue

                    # notify Socket's Node
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input:  socket.node.onInputChanged(socket)
                    if socket.is_output: socket.node.onOutputChanged(socket)

        except Exception as e: dumpException(e)


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


# Example: using validators for Edge
# You can register edge validators wherever you want, even here...
# However if you do use overridden Edge, you should call registerEdgeValidator on that overridden class
#
from datanodes.core.node_edge_validators import *
Edge.registerEdgeValidator(edge_validator_debug)
Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
