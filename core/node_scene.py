from graphics.graphics_scene import GraphicsScene

class Scene:
    def __init__(self):
        self.nodes = []
        self.edges = []

        self.scene_width  = 64000
        self.scene_height = 64000

        self.initUI()

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

    