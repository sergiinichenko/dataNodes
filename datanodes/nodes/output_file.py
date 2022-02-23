from stat import filemode
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *


class FileOutputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 140.0

class FileOutputContent(DataContent):
    def initUI(self):
        super().initUI()

        self.separator = "'"

        self.layout = QGridLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.openFile = QPushButton("Output file path")
        self.openFile.setStyleSheet("margin-bottom: 10px; height: 30px;")
        self.layout.addWidget(self.openFile, 0, 0, 1, 2)

        self.cb = QComboBox()
        self.cb.addItem(",")
        self.cb.addItem(".")
        self.cb.addItem(";")
        self.cb.addItem("tab")

        label = QLabel("Sep:  ", self)        
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        #self.cb.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(label, 1, 0)
        self.layout.addWidget(self.cb, 1, 1)

        self.cb.currentIndexChanged.connect(self.selectionchange)


        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setText("output.csv")
        self.layout.addWidget(self.edit, 2, 0, 1, 2)

    def selectionchange(self):
        self.setSeparator()
        self.changed.emit()
        
    def setSeparator(self):
        sep = self.cb.currentText()
        if sep == "," or sep == "." or sep == ";":
            self.node.separator = sep
            return
        if sep == "tab":
            self.node.separator = "\t"
            return
        self.node.separator = ""        

    def serialize(self):
        res = super().serialize()
        res['sel_ind'] = self.cb.currentIndex()
        res['file'] = self.node.file
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.cb.setCurrentIndex(data['sel_ind'])
            self.setSeparator()

            self.node.file = data['file']
            self.edit.setText(os.path.basename(self.node.file))
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_FILEOUTPUT)
class FileOutputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_FILEOUTPUT
    op_title = "File"

    def __init__(self, scene, inputs=[SOCKET_TYPE_DATA], outputs=[]):
        super().__init__(scene, inputs, outputs)
        #self.value = None
        self.can_write = True
        self.separator = ","
        self.file = ""
        self.setDirty()


    def initInnerClasses(self):
        self.content = FileOutputContent(self)
        self.grNode  = FileOutputGraphicsNode(self)
        self.properties = NodeProperties(self)
        self.content.openFile.clicked.connect(self.openOutputFile)
        self.content.openFile.clicked.connect(self.onInputChanged)
        self.content.changed.connect(self.reWriteFile)

    def reWriteFile(self):
        self.writeDFFile(self.file)

    def openOutputFile(self):
        file, filter = QFileDialog.getSaveFileName(self.scene.getView(), 'Save to file')

        if file == '':
            return
        else:
            self.file = file
            self.content.edit.setText(os.path.basename(self.file))
            self.can_write = True

    def writeDFFile(self, file):
        if self.hasValue(0):
            if file != "":
                try:
                    df = pd.DataFrame.from_dict(self.getInput(0).value)
                    df.to_csv(file, sep=self.separator, index=False)
                    self.can_write = True
                except Exception as e : 
                    dumpException(e)
                    self.can_write = False
        else:
            self.can_write = False
            
    def evalImplementation(self, silent=False):
        self.writeDFFile(self.file)
        if self.can_write : return True
        else: return True
