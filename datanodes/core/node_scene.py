from datanodes.core.utils import dumpException
from datanodes.graphics.graphics_scene import GraphicsScene
from datanodes.core.node_serializer import Serializer
from datanodes.core.node_node import Node
from datanodes.core.node_edge import Edge
from datanodes.core.node_socket import Socket
import json, os
from collections import OrderedDict
from datanodes.core.node_history import SceneHistory
from datanodes.core.node_clipboard import SceneClipboard


class InvalidFile(Exception): pass


class Scene(Serializer):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width  = 64000
        self.scene_height = 64000

        self._has_been_modified = False
        
        # initialize all listeners
        self._last_selected_items = None
        self._has_been_modified_listeners = []
        self._selected_listeners = []
        self._deselected_listeners = []

        # Store the callback for retrieving the needed Node class
        self.node_class_selector = None

        self.initUI()

        self.history   = SceneHistory(self)
        self.clipboard = SceneClipboard(self)
        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

    def initUI(self):
        # create the scene
        self.grScene = GraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)


    def onItemSelected(self):
        current_selected_items = self.selectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            self.history.storeHistory("Selection changed")
            for callback in self._selected_listeners: callback()


    def onItemsDeselected(self):
        self.resetLastSelectedStates()
        if self._last_selected_items is not None:
            self._last_selected_items = None
            self.history.storeHistory("Deselected everything")
            for callback in self._deselected_listeners: callback()


    def isModified(self):
        return self.has_been_modified

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:

            # set it now because it will be reading it soon
            self._has_been_modified = value

            for callback in self._has_been_modified_listeners : callback()

        self._has_been_modified = value


    # helper listener functions
    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback):
        self._deselected_listeners.append(callback)

    def addDragEnterListener(self, callback):
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.getView().addDropListener(callback)


    def isModified(self) -> bool:
        """Is this `Scene` dirty aka `has been modified` ?

        :return: ``True`` if `Scene` has been modified
        :rtype: ``bool``
        """
        return self.has_been_modified

    def selectedItems(self):
        return self.grScene.selectedItems()

    def setSelectionAll(self, selected = True):
        for node in self.nodes:
            node.grNode.setSelected(selected)
        for edge in self.edges:
            edge.grEdge.setSelected(selected)

    def selectAll(self):
        self.setSelectionAll(True)

    def deselectAll(self):
        self.setSelectionAll(False)

    def getView(self):
        return self.grScene.views()[0]

    def getItemAtPos(self, pos):
        return self.getView().itemAt(pos)

    # custom flag to detect node or edge has been selected
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._lastSelectedState = False
        for edge in self.edges:
            edge.grEdge._lastSelectedState = False


    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print("!W:", "Scene::removeNode", "Node is not in the list")

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("!W:", "Scene::removeEdge", "Edge is not in the list")


    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        self.has_been_modified = False


    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            print("Successful saving to a file:", filename)

            self.has_been_modified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            raw = file.read()
            try:
                data = json.loads(raw, encoding="utf-8")
                self.deserialize(data)
                self.has_been_modified = False

            except json.JSONDecodeError:
                raise InvalidFile("{0} is not valid json file".format(os.path.basename(filename)))

            except Exception as e : 
                dumpException(e)

    def getEdgeClass(self):
        """ Returns the class representing the edge"""
        return Edge

    def setNodeClassSelector(self, class_selecting_function):
        #
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data):
        if self.node_class_selector is None:
            return Node
        else:
            return self.node_class_selector(data)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        center = self.getView().mapToScene(self.getView().viewport().rect().center())
        return OrderedDict([
            ('id' , self.id),
            ('scene_widht'  , self.scene_width),
            ('scene_height' , self.scene_height),
            ('view_x'       , center.x()),
            ('view_y'       , center.y()),
            ('view_scale'   , self.getView().zoom),
            ('nodes'        , nodes),
            ("edges"        , edges),
        ])

    def deserialize(self, data, hashmap=[], restore_id=True):
        self.clear()
        hashmap = {}

        if restore_id: self.id = data['id']

        self.getView().centerOn(data['view_x'], data['view_y'])
        #self.getView().translate(data['view_x'], data['view_y'])
        scale = data['view_scale'] / self.getView().zoom

        self.getView().scale(scale, scale)
        self.getView().zoom = data['view_scale']


        # create nodes from data
        for node_data in data["nodes"]:
            #Node(self).deserialize(node_data, hashmap, restore_id)
            self.getNodeClassFromData(node_data)(self).deserialize(node_data, hashmap, restore_id)

        for edge_data in data["edges"]:
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        # create adges from data
        for node in self.nodes:
            node.update()

        return True