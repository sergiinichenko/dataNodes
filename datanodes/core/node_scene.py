from datanodes.graphics.graphics_scene import GraphicsScene
from datanodes.core.node_serializer import Serializer
from datanodes.core.node_node import Node
from datanodes.core.node_edge import Edge
from datanodes.core.node_socket import Socket
import json
from collections import OrderedDict
from datanodes.core.node_history import SceneHistory
from datanodes.core.node_clipboard import SceneClipboard

class Scene(Serializer):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width  = 64000
        self.scene_height = 64000

        self._has_been_modified = False
        self._has_been_modified_listeners = []

        self.initUI()

        self.history   = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value

            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value


    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)


    def initUI(self):
        # create the scene
        self.grScene = GraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

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
            data = json.loads(raw, encoding="utf-8")
            self.deserialize(data)

            self.has_been_modified = False
        print("Successful loading from a file:", filename)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())

        return OrderedDict([
            ('id' , self.id),
            ('scene_widht'  , self.scene_width),
            ('scene_height' , self.scene_height),
            ('nodes'        , nodes),
            ("edges"        , edges),
        ])

    def deserialize(self, data, hashmap=[], restore_id=True):
        self.clear()
        hashmap = {}

        if restore_id: self.id = data['id']

        # create nodes from data
        for node_data in data["nodes"]:
            Node(self).deserialize(node_data, hashmap, restore_id)

        for edge_data in data["edges"]:
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        # create adges from data

        
        return True