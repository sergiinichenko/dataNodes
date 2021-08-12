
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
import re
import copy


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
                self.appendOutput(SOCKET_DATA_TEXT, name)
                existing.extend([name])

        self.updateOutputsPos()

        self.grNode.height = (size+1) * self.socket_spacing + 2.0 * self.socket_spacing
        self.grNode.update()

        self.border_radius = 10.0
        self.padding       = 10.0
        self.title_height = 24.0
        self._hpadding     = 5.0
        self._vpadding     = 5.0

        x, y = self.grNode.width - 2.0 * self.grNode.padding, (size+1) * self.socket_spacing + 2.0 * self.socket_spacing - self.grNode.title_height - 2.0 * self.grNode.padding
        self.content.resize(x, y)


    def setSocketsNames(self):
        if len(self.value) == 0: 
            return None

        dnames  = ['DATA']
        dnames.extend(self.value)
        for socket, name in zip(self.getOutputs(), dnames):
            socket.label = name


    def evalImplementation(self):
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
        self.content = ResizableContent(self)
        self.grNode  = ResizableGraphicsNode(self)
        self.content.changed.connect(self.recalculateNode)

    def evalImplementation(self):
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
        self.width  = 160.0
        self.height = 80.0
        self.min_height = 80.0

class UpdateContent(ResizableContent):
    def serialize(self):
        res = super().serialize()
        res['height'] = self.node.grNode.height
        res['content-widht'] = self.size().width()
        res['content-height'] = self.size().height()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.grNode.height = data['height']
            self.resize(data['content-widht'], data['content-height'])
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
        self.content.changed.connect(self.recalculateNode)

    def evalImplementation(self):
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












class RenameGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 100.0
        self.min_height = 100.0

class RenameContent(DataContent):
    def initUI(self):
        super().initUI()
        self.labels_in = {}
        self.labels_out = {}
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)

    def appendPair(self, namein, nameout, onchangemethod=None):
        i = len(self.labels_in)
        self.labels_in[namein]  = QLabel(namein, self)
        self.labels_out[namein] = QLineEdit(nameout, self)
        self.labels_in[namein].setAlignment(Qt.AlignRight)
        self.labels_out[namein].setAlignment(Qt.AlignLeft)
        self.mainlayout.addWidget(self.labels_in[namein], i, 0)
        self.mainlayout.addWidget(self.labels_out[namein], i, 1)
        self.labels_out[namein].textChanged.connect(self.node.recalculateNode)

    def resize(self, x, y):
        super().resize(x, y)
        self.setFixedSize(x, y)

    def clearContent(self):
        while self.mainlayout.count():
            child = self.mainlayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.labels_in.clear()
        self.labels_out.clear()
        """
        self.mainlayout.setParent(None)
        self.mainlayout = QGridLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainlayout)
        """

    def removePair(self, key):
        self.mainlayout.removeWidget(self.labels_in[key])
        self.mainlayout.removeWidget(self.labels_out[key])
        self.labels_in.deleteLater()
        self.labels_out.deleteLater()
        self.labels_in  = None
        self.labels_out = None

    def serialize(self):
        res = super().serialize()
        res['map']            = self.node.map
        res['width']          = self.node.grNode.width
        res['height']         = self.node.grNode.height
        res['content-widht']  = self.size().width()
        res['content-height'] = self.size().height()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.map           = data['map']
            self.node.grNode.height = data['height']
            self.node.grNode.width  = data['width']
            self.resize(data['content-widht'], data['content-height'])
            for name in self.node.map:
                self.appendPair(name, self.node.map[name])
            return True & res
        except Exception as e: 
            dumpException(e)
        return True & res


@register_node(OP_MODE_DATA_RENAME)
class RenameNode(DataNode):
    icon = "icons/math.png"
    op_code = OP_MODE_DATA_RENAME
    op_title = "Rename"

    def __init__(self, scene, inputs=[1], outputs=[1]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.value = {}
        self.map   = {}
        self.out   = {}

    def initSettings(self):
        super().initSettings()
        self.input_socket_position  = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = RenameContent(self)
        self.grNode  = RenameGraphicsNode(self)
        self.content.changed.connect(self.recalculateNode)

    def resize(self):
        if not self.getInput(0):
            current_size = self.grNode.min_height + 1
        else:
            size = len(self.getInput(0).value)
            current_size = size * 30.0 + self.socket_bottom_margin + self.socket_top_margin

        padding_title = self.grNode.title_height + 2.0 * self.grNode.padding

        if current_size >= self.grNode.min_height:
            self.grNode.height = current_size
            x, y = self.grNode.width - 2.0 * self.grNode.padding, current_size - padding_title
            self.content.resize(x, y)
            self.grNode.update()
        
    def evalImplementation(self):
        input_edge = self.getInput(0)
        if not input_edge:
            self.setInvalid()
            self.e = "Does not have and intry Node"
            self.content.clearContent()
            self.resize()
            return False
        else:
            try:
                self.value = self.getInput(0).value
                self.out   = {}

                for name in self.value:
                    if name not in self.map:
                        self.map[name] = name
                        self.content.appendPair(name, name)
                        self.resize()
                
                for name in self.map:
                    if name not in self.content.labels_in:
                        self.content.appendPair(name, name)
                    self.map[name] = self.content.labels_out[name].text()

                for name in self.map:
                    self.out[self.map[name]] = self.value[name]
                    
                self.getOutput(0).value = self.out
                self.getOutput(0).type = "df"
                return True
            except Exception as e:
                self.setDirty(False)
                self.setInvalid(False)
                self.e = e
                self.getOutput(0).value = {}
                self.getOutput(0).type = "float"
                return False









class CleanGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 200.0
        self.height = 240.0

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
        self.dropNAN.toggle()
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

    def evalImplementation(self):
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
                                nansel = np.isnan(self.filtered[name])
                            else:
                                sel = np.isnan(self.filtered[name])
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
