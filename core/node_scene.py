from graphics.graphics_scene import GraphicsScene
from core.node_serializer import Serializer
from core.node_node import Node
from core.node_edge import Edge
from core.node_socket import Socket
import json
from collections import OrderedDict
from core.node_scene_history import SceneHistory

class Scene(Serializer):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width  = 64000
        self.scene_height = 64000

        self.initUI()

        self.history = SceneHistory(self)

    def initUI(self):
        # create the scene
        self.grScene = GraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()


    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        print("Successful saving to a file:", filename)

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            raw = file.read()
            data = json.loads(raw, encoding="utf-8")
            self.deserialize(data)
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

    def deserialize(self, data, hashmap=[]):
        self.clear()
        hashmap = {}

        # create nodes from data
        for node_data in data["nodes"]:
            Node(self).deserialize(node_data, hashmap)

        for edge_data in data["edges"]:
            Edge(self).deserialize(edge_data, hashmap)

        # create adges from data

        
        return True