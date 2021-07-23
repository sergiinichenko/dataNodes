from PyQt5.QtWidgets import QGraphicsView
from datanodes.core.utils import dumpException
from datanodes.core.node_edge import Edge, EDGE_BEZIER, EDGE_DIRECT
from datanodes.graphics.graphics_socket import GraphicsSocket
from datanodes.core.node_node import SOCKET_INPUT, SOCKET_OUTPUT

DEBUG = False

class EdgeDragging:
    def __init__(self, grView:'QGraphicsView'):
        self.grView            = grView
        self.drag_edge         = None
        self.drag_start_socket = None

    def getEdgeClass(self):
        """Helper function to get the Edge class using what Scene class provides"""
        return self.getScene().getEdgeClass()


    def getScene(self):
        return self.grView.grScene.scene


    def updateDestination(self, x:float, y:float):
        self.drag_edge.grEdge.setDestination(x, y)
        self.drag_edge.grEdge.update()


    def edgeDragStart(self, item):
        try:
            if DEBUG : print ("View:edgeDragStart ~ Start the dragging ")
            if DEBUG : print ("View:edgeDragStart ~    assign the start socket to :", item.socket)
            if DEBUG : print ("View:edgeDragStart ~    type of the socket :", item.socket.inout)

            self.drag_start_socket = item.socket
            self.drag_edge = self.getEdgeClass()(self.getScene(), item.socket, None)
            if DEBUG : print ("View:edgeDragStart ~    drag_edge :", self.drag_edge)
        except Exception as e : dumpException(e)


    def edgeDragEnd(self, item):
        """ Ends the drag mouse event between two sockets """
        self.grView.resetMode()

        self.drag_edge.remove(silent=True)
        if DEBUG : print("End draging edge")

        try:
            if type(item) is GraphicsSocket:

                # cannot connect the socket to itself
                if item.socket == self.drag_start_socket:
                    if DEBUG : print("View:edgeDragEnd ~ Cannot assign socket to itself")
                    return

                # cannot connect two sockets of the same type
                if item.socket.inout == self.drag_start_socket.inout:
                    if DEBUG : print("View:edgeDragEnd ~ Cannot assign two sockets of the same type")
                    return

                """ remove the edge if the socket is attached to an input socket
                and the socket already has an edge """
                if item.socket.is_input:
                    item.socket.clearEdges()
                    if DEBUG : print("View:edgeDragEnd ~ previous edge has been removed from the end socket")

                # cannot connect the socket to itself
                if self.drag_start_socket.is_input and self.drag_start_socket.hasEdges():
                    self.drag_start_socket.clearEdges()
                    if DEBUG : print("View:edgeDragEnd ~ Cannot assign socket to itself")


                """ remove the previous edge if there is one """
                new_edge = self.getEdgeClass()(self.getScene(), self.drag_start_socket, item.socket)
                if DEBUG : print("View:edgeDragEnd ~ Created the new adge ")
                new_edge.notifyOnConnection()
                    
                self.getScene().history.storeHistory("created new edge")
                return True 
        except Exception as e : dumpException(e)

        if DEBUG : print("View:edgeDragEnd ~ The socket was not assigned and is removed")
        return False

