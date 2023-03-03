from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit, QFileDialog

class FileInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180
        self.height = 140

class FileInputContent(DataContent):
    def initUI(self):
        super().initUI()

        self.separator  = "Add"
        self.whitespace = False

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.openFile = QPushButton("Open input file")
        self.openFile.setStyleSheet("margin-bottom: 10px; height: 30px;")
        self.layout.addWidget(self.openFile, 0, 0, 1, 2)

        self.cb = QComboBox()
        self.cb.addItem(",")
        self.cb.addItem(".")
        self.cb.addItem(";")
        self.cb.addItem("tab")
        self.cb.addItem("space")

        label = QLabel("Sep:  ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        #self.cb.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(label, 1, 0)
        self.layout.addWidget(self.cb, 1, 1)

        self.cb.currentIndexChanged.connect(self.selectionchange)


        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setReadOnly(True)
        self.edit.setText("File name")
        self.layout.addWidget(self.edit, 2, 0, 1, 2)

    def selectionchange(self):
        self.setSeparator()
        self.changed.emit()
        
    def setSeparator(self):
        sep = self.cb.currentText()
        if sep == "," or sep == "." or sep == ";":
            self.node.separator  = sep
            self.node.whitespace = False    
            return
        if sep == "tab":
            self.node.separator = "\t"
            self.node.whitespace = False    
            return
        if sep == "space":
            self.node.separator = None
            self.node.whitespace = True    
            return
        self.node.separator  = ""        
        self.node.whitespace = False    

    def serialize(self):
        res = super().serialize()
        self.node.checkFilePath(self.node.file)
        res['sel_ind'] = self.cb.currentIndex()
        res['file']    = self.node.file
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.cb.setCurrentIndex(data['sel_ind'])
            self.setSeparator()
            self.node.file = data['file']
            self.node.path = self.node.scene.path
            self.edit.setText(os.path.basename(self.node.file))
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_FILEINPUT)
class FileInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_FILEINPUT
    op_title = "File"

    def __init__(self, scene, inputs=[], outputs=[SOCKET_TYPE_DATA]):
        super().__init__(scene, inputs, outputs)
        #self.value = None
        self.can_read = True
        self.separator = ","
        self.whitespace = False
        self.file = ""
        self.path = ""
        self.setDirty()

    def checkFilePath(self, file):
        #if self.scene._saved_to_new_file:
        self.file = os.path.relpath(self.path + file, self.scene.path)
        self.path = self.scene.path
        #else:
        #    self.file = file

    def initInnerClasses(self):
        self.content = FileInputContent(self)
        self.grNode  = FileInputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.openFile.clicked.connect(self.openInputFile)
        self.content.openFile.clicked.connect(self.onInputChanged)
        self.content.changed.connect(self.rereadFile)

    def rereadFile(self):
        self.readDFFile(self.path + self.file)
        self.recalculateNode()

    def openInputFile(self):
        file, filter = QFileDialog.getOpenFileName(self.scene.getView(), 'Open Node-Tree from File')

        if file == '':
            return
        if os.path.isfile(file):
            self.path = ""
            self.checkFilePath(file)
            self.content.edit.setText(os.path.basename(self.file))
            self.readDFFile(self.path + self.file)
        else:
            self.getOutput(0).value = "NaN"
            self.getOutput(0).type  = 'none'
            self.can_read = False


    def readDFFile(self, file):
        try:
            if self.separator is not None:
                df = pd.read_csv(file, sep=self.separator, delim_whitespace=self.whitespace).to_dict('list')
            else:
                df = pd.read_csv(file, delim_whitespace=self.whitespace).to_dict('list')
            res = {}
            for name in df:
                res[name] = np.array(df[name])
            self.getOutput(0).value = res
            self.getOutput(0).type  = 'df'
            self.can_read = True
        except Exception as e : 
            dumpException(e)
            self.getOutput(0).value = "NaN"
            self.getOutput(0).type  = 'none'
            self.can_read = False


    def evalImplementation(self, silent=False):
        self.checkFilePath(self.file)
        self.readDFFile(self.path + self.file)
        if self.can_read : return True
        else: return False
