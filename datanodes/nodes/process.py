
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *

class SeparateDFGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 200.0

class SeparateDFContent(NodeContentWidget):
    def initUI(self):
        self.operation = "To Float"
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Data Separate")

    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res


    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.resize(data['content-widht'], data['content-height'])
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_SEP)
class SeparateDFNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_SEP
    op_title = "Data Separate"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP


    def initInnerClasses(self):
        self.content = SeparateDFContent(self)
        self.grNode  = SeparateDFGraphicsNode(self)


    def generateSockets(self, data, names=None):
        self.clearOutputs()        
        outputs = [SOCKET_DATA_TEXT for l in range(data.shape[1]+1)]
        dnames = ['DATA']
        if names is not None: dnames.extend(names)
        self.createOutputs(outputs, dnames)
        self.grNode.height = (data.shape[1]+1) * self.socket_spacing + 2.0 * self.socket_spacing
        self.grNode.update()

        self.border_radius = 10.0
        self.padding       = 10.0
        self.title_height = 24.0
        self._hpadding     = 5.0
        self._vpadding     = 5.0

        x, y = self.grNode.width - 2.0 * self.grNode.padding, (data.shape[1]+1) * self.socket_spacing + 2.0 * self.socket_spacing - self.grNode.title_height - 2.0 * self.grNode.padding
        self.content.resize(x, y)


    def evalImplementation(self):
        input_edge = self.getInput(0)

        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False

        else:
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
            self.e     = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            if DEBUG : print("PRCNODE_SEP: get input value and type")

            if self.type == "df":
                if DEBUG : print("PRCNODE_SEP: input is df")

                if len(self.outputs) != (self.value.shape[1]+1):
                    if DEBUG : print("PRCNODE_SEP: generate new sockets")
                    self.generateSockets(self.value, list(self.value.columns))
                    if DEBUG : print("PRCNODE_SEP: new sockets have been generated")

                self.outputs[0].value = self.value
                self.outputs[0].type  = "df"
                for i, socket in zip(range(len(self.outputs[1:])), self.outputs[1:]):
                    socket.value = self.value.iloc[:,i]
                    socket.type  = "df"
                    if DEBUG : print("PRCNODE_SEP: sockets have been filled with data and types")
            else:
                print("FALSE: ", self.value)
            return True







class CombineGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160.0
        self.height = 160.0

class CombineContent(NodeContentWidget):
    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("Data XY")

    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.resize(data['content-widht'], data['content-height'])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_COMBXY)
class CombineNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_COMBXY
    op_title = "Data Combine"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_CENTER

    def initInnerClasses(self):
        self.content = CombineContent(self)
        self.grNode  = CombineGraphicsNode(self)

    def freeInputSockets(self):
        
        self.inputs

    def appendNewSocket(self):
        self.appendInput(input=1)
        size = len(self.inputs)
        current_size = size * self.socket_spacing + 2.0 * self.socket_spacing
        self.grNode.height = current_size
        self.grNode.update()

        self.border_radius = 10.0
        self.padding       = 10.0
        self.title_height = 24.0
        self._hpadding     = 5.0
        self._vpadding     = 5.0

        padding_title = self.grNode.title_height + 2.0 * self.grNode.padding
        x, y = self.grNode.width - 2.0 * self.grNode.padding, current_size - padding_title
        self.content.resize(x, y)

    def sortSockets(self):
        sockets_full = []
        sockets_empty = []
        for socket in self.inputs:
            if socket.hasEdges():
                sockets_full.append(socket)
            else:
                sockets_empty.append(socket)

        for i, socket in zip(range(len(sockets_full + sockets_empty)), sockets_full + sockets_empty):
            socket.index = i
            socket.setPos()

        self.inputs = sockets_full + sockets_empty
        self.removeFreeInputs()
        self.appendNewSocket()

    def generateNewSocket(self):
        if self.freeSockets() < 0:
            self.appendNewSocket()

        if self.freeSockets() > 1:
            self.removeFreeInputs()
            self.appendNewSocket()

    def getSocketsNames(self):
        input_sockets = self.inputs
        if len(input_sockets) == 0: return None
        for socket in input_sockets:
            if socket.hasEdges():
                edge = socket.edges[0]
                other_socket = edge.getOtherSocket(socket)
                if isinstance(other_socket.value, pd.Series):                
                    socket.label = other_socket.value.name

    def evalImplementation(self):
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            self.getSocketsNames()
            self.generateNewSocket()
            if len(input_edges) > 0:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = pd.DataFrame()
                for input in input_edges:
                    try:
                        if isinstance(input.value, pd.Series):
                            self.value[input.value.name] = pd.Series(input.value.values)

                        if isinstance(input.value, pd.DataFrame):
                            for name in input.value.columns:
                                self.value[name] = pd.Series(input.value[name].values)
                    except Exception as e:
                        self.e = e
                        dumpException(e)
                        
                self.outputs[0].value = self.value
                self.outputs[0].type = "df"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.outputs[0].value = 0
                self.outputs[0].type = "float"
                return False





class CleanGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 200.0

class CleanContent(NodeContentWidget):
    def initUI(self):
        self.layout = QVBoxLayout()

        self.dropNAN = QCheckBox('Drop NAN', self)
        self.dropNAN.toggle()
        self.dropNAN.stateChanged.connect(self.recalculate)

        self.dropINF = QCheckBox('Drop INF', self)
        self.dropINF.toggle()
        self.dropINF.stateChanged.connect(self.recalculate)

        self.dropSTR = QCheckBox('Drop Strings', self)
        self.dropSTR.toggle()
        self.dropSTR.stateChanged.connect(self.recalculate)

        self.removeSTR = QCheckBox('Remove sub-strings', self)
        self.removeSTR.toggle()
        self.removeSTR.stateChanged.connect(self.recalculate)

        self.layout.addWidget(self.dropINF)
        self.layout.addWidget(self.dropSTR)
        self.layout.addWidget(self.removeSTR)
        self.layout.addWidget(self.dropNAN)

        self.setLayout(self.layout)
        self.setWindowTitle("Data Clean")
    
    def recalculate(self):
        self.node.recalculate = True
        self.node.eval()

    def serialize(self):
        res = super().serialize()
        res['dropNAN'] = self.dropNAN.isChecked()
        res['dropINF'] = self.dropINF.isChecked()
        res['dropSTR'] = self.dropSTR.isChecked()
        res['removeSTR'] = self.removeSTR.isChecked()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.dropINF.setChecked(data['dropINF'])
            self.dropSTR.setChecked(data['dropSTR'])
            self.removeSTR.setChecked(data['removeSTR'])
            self.dropNAN.setChecked(data['dropNAN'])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_CLEAN)
class CleanNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_CLEAN
    op_title = "Data Clean"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def initInnerClasses(self):
        self.content = CleanContent(self)
        self.grNode  = CleanGraphicsNode(self)

    def toFloat(self, x):
        try:
            return float(x)
        except:
            return np.nan
    

    def evalImplementation(self):
        input_edge = self.getInput(0)

        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            print("Eveluation of the CLEAN node")
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
            self.e     = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            if DEBUG : print("PRCNODE_SEP: get input value and type")

            if isinstance(self.value, pd.DataFrame) or self.type == "df":
                if self.content.dropINF.isChecked():
                    self.value.replace([np.inf, -np.inf], np.nan, inplace=True)

                if self.content.dropSTR.isChecked():
                    self.value = self.value.applymap(self.toFloat)

                if self.content.removeSTR.isChecked():
                    self.value = self.value.applymap(str)
                    for name in self.value.columns:
                        self.value[name].str.replace(r'\D', '')
                    self.value = self.value.applymap(self.toFloat)

                if self.content.dropNAN.isChecked():
                    self.value.dropna(inplace = True)

                self.outputs[0].value = self.value
                self.outputs[0].type  = "df"
            else:
                print("FALSE: ", self.value)
            return True

