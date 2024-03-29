

from typing import OrderedDict
from datanodes.graphics.graphics_edge import GraphicsEdge
from datanodes.graphics.graphics_node import GraphicsNode
from datanodes.core.node_node import  Node
from datanodes.core.node_edge import  Edge
from datanodes.core.node_content_widget import NodeContentWidget
import json

DEBUG = False

class SceneClipboard():
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        if DEBUG : print("-- Copy to clipboard -- ")

        sel_nodes, sel_edges, sel_sockets, sel_data = [], [], {}, []

        for item in self.scene.selectedItems():
            """
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket
            """
            if isinstance(item, GraphicsNode):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket

            elif isinstance(item, NodeContentWidget):
                sel_data.append(item.onCopy())
            
            elif isinstance(item, GraphicsEdge):
                sel_edges.append(item.edge)

        # remove all the edges which are not connected to a node
        # in our list 
        edges_to_remove = []

        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                pass
            else:
                if DEBUG : print("edge", edge, " is not connected with both sides")
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            sel_edges.remove(edge)

        # make final list of edges
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        data = OrderedDict({
            'nodes' : sel_nodes, 
            'edges' : edges_final,
            'data'  : sel_data,
        })

        # If cut the items then delete them from the main scene
        if delete : 
            self.scene.getView().deleteSelectedItem()
            
            # store the history
            self.scene.history.storeHistory('Cut out elements')

        return data

    def deserializeFromClipboard(self, raw_data, setSelected=False):
        try:
            data = json.loads(raw_data)
            hashmap = {}

            # calculate the mouse pointer - scene postion
            view      = self.scene.getView()
            mouse_pos = view.last_scene_mouse_position

            # calculate selected objects bounding box and its center
            minx, maxx, miny, maxy = 10000000,-10000000, 10000000,-10000000
            x = 0.0
            y = 0.0
            for node_data in data['nodes']:
                x, y = node_data['pos_x'], node_data['pos_y']
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y

            # add width and height of a node
            maxx -= 180
            maxy += 100

            relbboxcenterx = (minx + maxx) / 2 - minx
            relbboxcentery = (miny + maxy) / 2 - miny

            # calculate the offset of the newly creating nodes
            mousex, mousey = mouse_pos.x(), mouse_pos.y()

            # calculate the offset of the newly created nodes
            offset_x = mouse_pos.x() - x
            offset_y = mouse_pos.y() - y
            self.scene.new_nodes    = []
            # Create each node
            if 'nodes' in data:
                for node_data in data['nodes']:
                    new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
                    new_node.deserialize(node_data, hashmap, restore_id=False)
                    # shift the new nodes position
                    pos = new_node.pos
                    posx, posy = new_node.pos.x(), new_node.pos.y()
                    newx, newy = mousex + posx - minx, mousey + posy - miny
                    new_node.setPos(newx, newy)
                    new_node.grNode.setSelected(setSelected)
                    self.scene.new_nodes.append(new_node)

            # Create each edge
            if 'edges' in data:
                for edge_data in data['edges']:
                    Edge(self.scene).deserialize(edge_data, hashmap, restore_id=False)
                    #new_edge.deserialize(edge_data, hashmap, restore_id=False)
                    #new_edge.grEdge.setSelected(setSelected)

            # Paste the data
            if 'data' in data:
                for data_data in data['data']:
                    for item in self.scene.selectedItems():
                        if isinstance(item, NodeContentWidget):
                            item.onPaste(data_data)

            # only the input nodes will receive the eval signal
            #if nodes is not None:
            #    for node in nodes:
            #        if node.id in hashmap:
            #            if not node.hasValue():
            #                node.update(silent=True)
                            
        except ValueError as e:
            # try to paste data into the node
            for item in self.scene.selectedItems():
                if isinstance(item, NodeContentWidget):
                    item.onPaste(raw_data)
        
