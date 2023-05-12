
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import re
import copy
from PyQt5.QtWidgets import QCheckBox, QLabel, QLineEdit

@register_node(OP_MODE_DATA_SEP)
class SeparateNode(ResizableOutputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_SEP
    op_title = "Separate"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP


    def initInnerClasses(self):
        self.content = ResizableContent(self)
        self.grNode  = ResizableGraphicsNode(self)
        self.properties = NodeProperties(self)

    def generateSockets(self):
        dnames  = ['DATA']
        dnames.extend(list(self.value.keys()))
        size = len(self.value)

        existing = []
        if self.getOutputs():
            existing = [soket.label for soket in self.getOutputs()]

            # remove the socket from the node if the socket is not in the input data
            for name in existing:
                if name not in dnames and name is not None:
                    soket = self.getOutputByLabel(name)
                    soket.remove()

            # remove sockets without labels:
            for soket in self.getOutputs():
                if soket.label is None : soket.remove()

        # append a socket with a label if the label does not exist
        for name in dnames:
            if name not in existing:
                self.appendOutput(SOCKET_TYPE_VALUE, name)
                existing.extend([name])

        self.updateOutputsPos()

        self.grNode.height = (size+1) * self.socket_spacing + 2.0 * self.socket_spacing
        self.grNode.update()

        self.border_radius = 10
        self.padding       = 10
        self.title_height = 24
        self._hpadding     = 5
        self._vpadding     = 5
        self.content.updateSize()


    def setSocketsNames(self):
        if len(self.value) == 0: 
            return None

        dnames  = ['DATA']
        dnames.extend(self.value)
        for socket, name in zip(self.getOutputs(), dnames):
            socket.label = name


    def evalImplementation(self, silent=False):
        input_edge = self.getInput(0)

        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.clearOutputs()        
            return False

        else:
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
            self.e     = ""
            self.value = input_edge.value
            self.type  = input_edge.type
            if DEBUG : print("PRCNODE_SEP: get input value and type")
            if isinstance(self.value, dict):
                if DEBUG : print("PRCNODE_SEP: input is df")

                if not silent:
                    if len(self.outputs) != (len(self.value)+1):
                        if DEBUG : print("PRCNODE_SEP: generate new sockets")
                        self.generateSockets()
                        if DEBUG : print("PRCNODE_SEP: new sockets have been generated")
                    else:
                        self.setSocketsNames()

                self.getOutput(0).value = self.value
                self.getOutput(0).type  = "df"
                for name, socket in zip(self.value, self.getOutputs()[1:]):
                    socket.value = {name : self.value[name]}
                    socket.type  = "df"
                    if DEBUG : print("PRCNODE_SEP: sockets have been filled with data and types")
            else:
                print("FALSE: ", self.value)
            return True







@register_node(OP_MODE_DATA_COMBXY)
class CombineNode(ResizableInputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_COMBXY
    op_title = "Combine"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def onInputChange(self, new_edge=None):
        self.content.changed.emit()

    def initInnerClasses(self):
        self.content    = ResizableContent(self)
        self.grNode     = ResizableGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def evalImplementation(self, silent=False):
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            self.getSocketsNames()
            if len(input_edges) > 0:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = {}
                for input in input_edges:
                    try:
                        if isinstance(input.value, dict):
                            for name in input.value:
                                try:
                                    self.value[name] = input.value[name].copy()
                                except:
                                    self.value[name] = input.value[name]

                        if isinstance(input.value, pd.Series):
                            self.value[input.value.name] = pd.Series(input.value.values)

                        if isinstance(input.value, pd.DataFrame):
                            for name in input.value.columns:
                                self.value[name] = pd.Series(input.value[name].values)
                    except Exception as e:
                        self.e = e
                        dumpException(e)
                        
                self.getOutput(0).value = self.value
                self.getOutput(0).type = "df"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.getOutput(0).value = 0
                self.getOutput(0).type = "float"
                return False







class UpdateGraphicsNode(ResizableGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 80
        self.min_height = 80

class UpdateContent(ResizableContent):
    def serialize(self):
        res = super().serialize()
        res['height'] = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.updateSize()
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_UPDATE)
class UpdateNode(ResizableInputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_UPDATE
    op_title = "Update"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def onInputChange(self, new_edge=None):
        self.content.changed.emit()

    def initInnerClasses(self):
        self.content = UpdateContent(self)
        self.grNode  = UpdateGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.changed.connect(self.recalculateNode)

    def evalImplementation(self, silent=False):
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            self.getSocketsNames()
            if len(input_edges) > 0:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e = ""
                self.value = {}
                for input in input_edges:
                    try:
                        if isinstance(input.value, dict):
                            for name in input.value:
                                try:
                                    self.value[name] = input.value[name].copy()
                                except:
                                    self.value[name] = input.value[name]

                        if isinstance(input.value, pd.Series):
                            self.value[input.value.name] = pd.Series(input.value.values)

                        if isinstance(input.value, pd.DataFrame):
                            for name in input.value.columns:
                                self.value[name] = pd.Series(input.value[name].values)
                    except Exception as e:
                        self.e = e
                        dumpException(e)
                        
                self.getOutput(0).value = self.value
                self.getOutput(0).type = "df"
                return True
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.getOutput(0).value = 0
                self.getOutput(0).type = "float"
                return False









class RenameGraphicsNode(ResizableGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200
        self.height = 80
        self.min_height = 80


class RenameContent(ResizableContent):
    def initUI(self):
        super().initUI()
        self.labels_in  = {}
        self.labels_out = {}
        self.mainlayout.setContentsMargins(5,5,5,5)
        self.mainlayout.setAlignment(Qt.AlignTop)
        #self.mainlayout.setSpacing(0)
        self.map       = {}
        self.history   = {}

    def getSize(self, dic):
        size = 0
        for name in dic:
            size += len(dic[name])
        return size

    def appendPair(self, id, namein, nameout, onchangemethod=None):
        i = self.getSize(self.labels_in)
        
        if str(id) not in self.labels_in  : self.labels_in[str(id)]  = {}
        if str(id) not in self.labels_out : self.labels_out[str(id)] = {}
        if str(id) not in self.map        : self.map[str(id)]        = {}
        
        self.labels_in[str(id)][namein]  = QLabel(namein, self)
        self.labels_out[str(id)][namein] = QLineEdit(nameout, self)
        self.labels_in[str(id)][namein].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.labels_out[str(id)][namein].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.labels_in[str(id)][namein], i, 0)
        self.mainlayout.addWidget(self.labels_out[str(id)][namein], i, 1)
        self.map[str(id)][namein] = nameout

        self.labels_out[str(id)][namein].returnPressed.connect(lambda: self.renameData(str(id), namein, self.labels_out[str(id)][namein] ) )
        
    def renameData(self, id_str, namein, nameout):
        pair = Pair(self.map[id_str][namein], nameout.text(), self.getSize(self.map))
        print("Initial ", self.node._title)
        print("id_str  ", id_str)
        self.map[id_str][namein] = nameout.text()
        self.renamed.emit(pair)


    def removePair(self, socket):

        if str(socket.id) in self.map:
            for name in list(self.map[str(socket.id)]):
                self.mainlayout.removeWidget(self.labels_in[ str(socket.id)][name])
                self.mainlayout.removeWidget(self.labels_out[str(socket.id)][name])
                self.labels_in[ str(socket.id)][name].setParent(None)
                self.labels_out[str(socket.id)][name].setParent(None)
                del self.labels_in[ str(socket.id)][name]
                del self.labels_out[str(socket.id)][name]
                del self.map[str(socket.id)][name]

        if self.labels_in[str(socket.id)]   == {} : del self.labels_in[str(socket.id)]
        if self.labels_out[str(socket.id)]  == {} : del self.labels_out[str(socket.id)]
        if self.map[str(socket.id)]         == {} : del self.map[str(socket.id)]

        self.sortWidgets()

    def sortWidgets(self):
        for key in self.labels_in:
            for i, name in enumerate(self.labels_in[key]):
                self.labels_in[key][name].setParent(None)
                self.labels_out[key][name].setParent(None)

        i = 0
        for key in self.labels_in:
            for name in self.labels_in[key]:
                self.mainlayout.addWidget(self.labels_in[key][name],   i, 0)
                self.mainlayout.addWidget(self.labels_out[key][name], i, 1)
                i = i + 1

        self.node.resize()


    def clearContent(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels_in  = {}
        self.labels_out = {}

    def serialize(self):
        res = super().serialize()
        res['map']            = self.map
        res['width']          = self.node.grNode.width
        res['height']         = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.map                = data['map']
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.updateSize()
            for id in self.map:
                for namein in self.map[id]:
                    self.appendPair(id, namein, self.map[id][namein])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_RENAME)
class RenameNode(ResizableInputNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_RENAME
    op_title = "Rename"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.value = {}
        self.out   = {}

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_top_margin      = 44
        self.socket_spacing         = 27

    def initInnerClasses(self):
        self.content    = RenameContent(self)
        self.grNode     = RenameGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.removed.connect(self.removeInnput)
        self.content.changed.connect(self.recalculateNode)
        self.content.renamed.connect(self.rename)
        
    def removeInnput(self, socket=None):
        self.content.removePair(socket)
        self.recalculateNode()

    def onInputChange(self, new_edge=None):
        self.content.changed.emit()

    def getSocketsNames(self):
        #need to remove the sockets labels
        pass
    
    def resize(self):
        size  = self.content.getSize(self.content.labels_in)
        current_size = (size) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin

        if current_size > self.grNode.min_height:
            self.grNode.height = current_size
            self.grNode.update()
            self.content.updateSize()
        
    def evalImplementation(self, silent=False):
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            if len(input_edges) > 0:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e     = ""
                self.value = {}
                try:
                    for input in input_edges:
                        if str(input.id) not in self.content.map : self.content.map[str(input.id)] = {}
                        
                        for name in input.value:
                            if name not in self.content.map[str(input.id)]:
                                self.content.appendPair(input.id, name, name)

                        """
                        for name in self.content.map[str(input.id)]:
                            self.content.map[str(input.id)][name] = self.content.labels_out[str(input.id)][name].text()
                        """

                        for name in input.value:
                            self.value[self.content.map[str(input.id)][name]] = input.value[name]

                        self.resize()
                                
                    self.getOutput(0).value = self.value
                    self.getOutput(0).type = "df"
                    return True
                except Exception as e:
                    self.e = e
                    dumpException(e)
                    return False
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.getOutput(0).value = 0
                self.getOutput(0).type = "float"
                return False














class CleanGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200
        self.height = 240

class CleanContent(DataContent):
    def initUI(self):
        super().initUI()
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)

        self.dropSTR = QCheckBox('String to NAN', self)
        self.dropSTR.toggle()
        self.dropSTR.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.dropSTR, 0, 0, 1, 2)

        self.removeSTR = QCheckBox('Remove sub-strings', self)
        self.removeSTR.toggle()
        self.removeSTR.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.removeSTR, 1, 0, 1, 2)

        self.strToNum = QCheckBox('String to ', self)
        self.strToNum.toggle()
        self.strToNum.stateChanged.connect(self.recalculate)
        self.strToNumValue = QLineEdit("0.0", self)
        self.strToNumValue.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.strToNum, 2, 0)
        self.mainlayout.addWidget(self.strToNumValue, 2, 1)

        self.infToNum = QCheckBox('INF to ', self)
        self.infToNum.toggle()
        self.infToNum.stateChanged.connect(self.recalculate)
        self.infToNumValue = QLineEdit("0.0", self)
        self.infToNumValue.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.infToNum, 3, 0)
        self.mainlayout.addWidget(self.infToNumValue, 3, 1)

        self.dropINF = QCheckBox('INF to NAN', self)
        self.dropINF.toggle()
        self.dropINF.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.dropINF, 4, 0, 1, 2)

        self.nanToNum = QCheckBox('NAN to ', self)
        self.nanToNum.toggle()
        self.nanToNum.stateChanged.connect(self.recalculate)
        self.nanToNumValue = QLineEdit("0.0", self)
        self.nanToNumValue.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.nanToNum, 5, 0)
        self.mainlayout.addWidget(self.nanToNumValue, 5, 1)

        self.dropNAN = QCheckBox('Drop NAN', self)
        #self.dropNAN.toggle()
        self.dropNAN.stateChanged.connect(self.recalculate)
        self.mainlayout.addWidget(self.dropNAN, 6, 0, 1, 2)

        self.setWindowTitle("Data Clean")
    
    def recalculate(self):
        self.node.recalculate = True
        self.node.eval()

    def serialize(self):
        res = super().serialize()
        res['dropSTR']        = self.dropSTR.isChecked()
        res['removeSTR']      = self.removeSTR.isChecked()
        res['strToNum']       = self.strToNum.isChecked()
        res['strToNumValue']  = self.strToNumValue.text()
        res['infToNum']       = self.infToNum.isChecked()
        res['infToNumValue']  = self.infToNumValue.text()
        res['dropINF']        = self.dropINF.isChecked()
        res['nanToNum']       = self.nanToNum.isChecked()
        res['nanToNumValue']  = self.nanToNumValue.text()
        res['dropNAN']        = self.dropNAN.isChecked()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.dropSTR.setChecked(data['dropSTR'])
            self.removeSTR.setChecked(data['removeSTR'])
            self.strToNum.setChecked(data['strToNum'])
            self.strToNumValue.setText(data['strToNumValue'])
            self.infToNum.setChecked(data['infToNum'])
            self.infToNumValue.setText(data['infToNumValue'])
            self.dropINF.setChecked(data['dropINF'])
            self.nanToNum.setChecked(data['nanToNum'])
            self.nanToNumValue.setText(data['nanToNumValue'])
            self.dropNAN.setChecked(data['dropNAN'])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_CLEAN)
class CleanNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_CLEAN
    op_title = "Clean"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def initInnerClasses(self):
        self.content = CleanContent(self)
        self.grNode  = CleanGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.nanToNumValue.returnPressed.connect(self.recalculate)
        self.content.strToNumValue.returnPressed.connect(self.recalculate)
        self.content.infToNumValue.returnPressed.connect(self.recalculate)
        self.content.changed.connect(self.recalculate)

    def recalculate(self):
        self.setDirty()
        self.eval()

    def toFloat(self, x):
        try:
            return float(x)
        except:
            return np.nan

    def isString(self, x):
        try:
            float(x)
            return False
        except:
            return True

    def onlyNumerics(self, seq):
        return re.sub("[^\d\.]", "", seq)

    def evalImplementation(self, silent=False):
        input_socket = self.getInput(0)

        if not input_socket:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.setDirty(False)
            self.setInvalid(False)
            if DEBUG : print("PRCNODE_SEP: reset dirty and invalid")
            self.e     = ""
            self.value = input_socket.value
            self.type  = input_socket.type
            if DEBUG : print("PRCNODE_SEP: get input value and type")
            self.filtered = {}

            try:
                self.e = ""
                if isinstance(self.value, dict):
                    self.filtered = copy.deepcopy(self.value)

                    if self.content.dropSTR.isChecked():
                        for name in self.filtered:
                            self.filtered[name] = np.array(list(map(self.toFloat, self.filtered[name])))

                    if self.content.removeSTR.isChecked():
                        for name in self.filtered:
                            self.filtered[name] = np.array(list(map(self.onlyNumerics, self.filtered[name].astype('str'))))
                            self.filtered[name] = np.array(list(map(self.toFloat, self.filtered[name])))

                    if self.content.strToNum.isChecked():
                        val = float(self.content.strToNumValue.text())
                        for name in self.filtered:
                            sel = np.array(list(map(self.isString, self.filtered[name])))
                            self.filtered[name][sel] = val
                            self.filtered[name] = np.array(list(map(self.toFloat, self.filtered[name])))

                    if self.content.infToNum.isChecked():
                        val = float(self.content.infToNumValue.text())
                        for name in self.filtered:
                            self.filtered[name][np.isinf(self.filtered[name])] = val

                    if self.content.dropINF.isChecked():
                        for name in self.filtered:
                            self.filtered[name][np.isinf(self.filtered[name])] = np.nan

                    if self.content.nanToNum.isChecked():
                        val = float(self.content.nanToNumValue.text())
                        for name in self.filtered:
                            self.filtered[name][np.isnan(self.filtered[name])] = val

                    if self.content.dropNAN.isChecked():
                        nansel = None
                        for name in self.filtered:
                            if nansel is None:
                                nansel = ~np.isnan(self.filtered[name])
                            else:
                                sel = ~np.isnan(self.filtered[name])
                                nansel = np.logical_and(nansel, sel)
                        for name in self.filtered:
                            self.filtered[name] = self.filtered[name][nansel]




                elif isinstance(self.value, pd.DataFrame):
                    self.filtered = copy.deepcopy(self.value)

                    if self.content.dropINF.isChecked():
                        self.filtered.replace([np.inf, -np.inf], np.nan, inplace=True)

                    if self.content.dropSTR.isChecked():
                        self.filtered = self.filtered.applymap(self.toFloat)

                    if self.content.removeSTR.isChecked():
                        self.filtered = self.filtered.applymap(str)
                        for name in self.filtered.columns:
                            self.filtered[name].str.replace(r'\D', '')
                        self.filtered = self.filtered.applymap(self.toFloat)

                    if self.content.dropNAN.isChecked():
                        self.filtered.dropna(inplace = True)

                else:
                    self.setDirty(False)
                    self.setInvalid(False)
                    self.e = "Not suotable format of the input data"
                    self.getOutput(0).value = {0.0}
                    self.getOutput(0).type = "float"
                    return False

                self.getOutput(0).value = self.filtered
                self.getOutput(0).type  = "df"
                return True

            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = e
                self.getOutput(0).value = {0.0}
                self.getOutput(0).type = "float"
                return False







class SelectGraphicsNode(ResizableGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 160
        self.height = 80
        self.min_height = 80

class SelectContent(ResizableContent):
    def initUI(self):
        super().initUI()
        self.mainlayout.setContentsMargins(5,5,5,5)
        self.mainlayout.setAlignment(Qt.AlignTop)
        self.select_map    = {}
        self.checkbox_map  = {}
        self.labels_map    = {}
        self.position      = 0

    def getSize(self, dic):
        size = 0
        for name in dic:
            size += len(dic[name])
        return size

    def if_contains(self, name):
        for id in self.select_map:
            if name in self.select_map[id]:
                return True
        return False
        

    def appendPair(self, id, name, value=False):
        i = self.getSize(self.labels_map)
        
        if str(id) not in self.labels_map   : self.labels_map[str(id)]   = {}
        if str(id) not in self.checkbox_map : self.checkbox_map[str(id)] = {}
        if str(id) not in self.select_map   : self.select_map[str(id)]   = {}

        self.labels_map[str(id)][name]   = QLabel(name, self)
        self.labels_map[str(id)][name].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.labels_map[str(id)][name].setStyleSheet("margin-right: 10px;")
        self.mainlayout.addWidget(self.labels_map[str(id)][name], i, 0, 1, 4)

        self.checkbox_map[str(id)][name] = QCheckBox("")
        self.checkbox_map[str(id)][name].setChecked(value)
        self.mainlayout.addWidget(self.checkbox_map[str(id)][name], i, 5, 1, 1)

        self.checkbox_map[str(id)][name].stateChanged.connect(self.updateMaps)
        self.select_map[str(id)][name] = value


    def updateMaps(self):
        for id in self.select_map:
            for name in self.select_map[id]:
                self.select_map[id][name] = self.checkbox_map[id][name].isChecked()
        self.node.recalculateNode()

    def removePair(self, id, name):
        if id == None : return
        if str(id) in self.select_map:
            self.mainlayout.removeWidget(self.labels_map[ str(id)][name])
            self.mainlayout.removeWidget(self.checkbox_map[str(id)][name])
            self.labels_map[ str(id)][name].setParent(None)
            self.checkbox_map[str(id)][name].setParent(None)
            del self.labels_map[ str(id)][name]
            del self.checkbox_map[str(id)][name]
            del self.select_map[str(id)][name]

            if self.labels_map[str(id)]   == {} : del self.labels_map[str(id)]
            if self.checkbox_map[str(id)] == {} : del self.checkbox_map[str(id)]
            if self.select_map[str(id)]   == {} : del self.select_map[str(id)]

        self.sortWidgets()

    def sortWidgets(self):
        for key in self.labels_map:
            for i, name in enumerate(self.labels_map[key]):
                self.labels_map[key][name].setParent(None)
                self.checkbox_map[key][name].setParent(None)

        i = 0
        for key in self.labels_map:
            for name in self.labels_map[key]:
                self.mainlayout.addWidget(self.labels_map[key][name],   i, 0, 1, 4)
                self.mainlayout.addWidget(self.checkbox_map[key][name], i, 5, 1, 1)
                i = i + 1
        self.node.resize()


    def clearContent(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels_map   = {}
        self.checkbox_map = {}

    def serialize(self):
        res = super().serialize()
        res['map']            = self.select_map
        res['width']          = self.node.grNode.width
        res['height']         = self.node.grNode.height
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.select_map         = data['map']
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.updateSize()
            for id in self.select_map:
                for name in self.select_map[id]:
                    self.appendPair(id, name, self.select_map[id][name])
                    
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_SELECT)
class SelectNode(ResizableInputNode):
    icon     = "icons/math.png"
    op_code  = OP_MODE_DATA_SELECT
    op_title = "Select"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.value = {}
        self.out   = {}

    def getValueSize(self):
        return len(self.input_names)

    def updateNames(self, dict):
        for id in self.content.select_map:
            if dict.old in self.content.select_map[id]:
                self.content.labels_map[id]   = {dict.new if k == dict.old else k : v for k, v in self.content.labels_map[id].items()}
                self.content.checkbox_map[id] = {dict.new if k == dict.old else k : v for k, v in self.content.checkbox_map[id].items()}
                self.content.select_map[id]   = {dict.new if k == dict.old else k : v for k, v in self.content.select_map[id].items()}
                self.content.labels_map[id][dict.new].setText(dict.new)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP
        self.socket_top_margin      = 44
        self.socket_spacing         = 25

    def initInnerClasses(self):
        self.content    = SelectContent(self)
        self.grNode     = SelectGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.removed.connect(self.removeInnput)
        self.content.changed.connect(self.recalculateNode)

    def removeInnput(self, socket=None):
        if str(socket.id) in self.content.select_map:
            for name in list(self.content.select_map[str(socket.id)]):
                self.content.removePair(socket.id, name)
        self.recalculateNode()

    def onInputChange(self, new_edge=None):
        self.content.changed.emit()

    def getSocketsNames(self):
        #need to remove the sockets labels
        pass
    
    def resize(self):
        values  = self.content.getSize(self.content.labels_map)
        sockets = len(self.getInputs()) - 1
        size    = max(values, sockets)
        current_size = (size) * self.socket_spacing + self.socket_bottom_margin + self.socket_top_margin

        if current_size > self.grNode.min_height:
            self.grNode.height = current_size
            self.grNode.update()
            self.content.updateSize()

        
    def evalImplementation(self, silent=False):
        input_edges = self.getInputs()
        if not input_edges:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            return False
        else:
            self.sortSockets()
            if len(input_edges) > 0:      
                self.setDirty(False)
                self.setInvalid(False)
                self.e     = ""
                self.value = {}
                self.input_names = []
                
                try:
                    for input in input_edges:
                        if input.value == None : continue
                        self.input_names.extend(list(input.value))
                        

                    for input in input_edges:
                        if input.value == None : continue
                        
                        # Append pair if not there yet                        
                        for name in input.value:
                            # if name not in self.content.select_map[str(input.id)]:
                            if not self.content.if_contains(name):
                                self.content.appendPair(input.id, name)
                                self.value[name] = input.value[name]

                        # Remove the pair if it is not in the input or renamed
                        if str(input.id) in self.content.select_map:
                            for name in list(self.content.select_map[str(input.id)]):
                                # if name not in self.content.select_map[str(input.id)]:
                                if name not in self.input_names:
                                    self.content.removePair(input.id, name)
                        
                        for name in input.value:
                            if str(input.id) in self.content.select_map:
                                if self.content.select_map[str(input.id)][name]:
                                    self.value[name] = input.value[name]

                        self.resize()

                    self.getOutput(0).value = self.value
                    self.getOutput(0).type = "df"
                    return True
                except Exception as e:
                    self.e = e
                    dumpException(e)
                    return False
            else:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = "Not enough input data"
                self.getOutput(0).value = 0
                self.getOutput(0).type = "float"
                return False