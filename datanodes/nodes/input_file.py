from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *


class FileInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 180.0
        self.height = 120.0

class FileInputContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.openFile = QPushButton("Open input file")
        self.layout.addWidget(self.openFile)

        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setReadOnly(True)
        self.edit.setText("File name")
        self.layout.addWidget(self.edit)


    def serialize(self):
        res = super().serialize()
        res['file'] = self.node.file
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.node.file = data['file']
            self.edit.setText(os.path.basename(self.node.file))
            self.node.readDFFile(self.node.file)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_FILEINPUT)
class FileInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_FILEINPUT
    op_title = "Input file"

    def __init__(self, scene, inputs=[], outputs=[SOCKET_DATA_NUMERIC]):
        super().__init__(scene, inputs, outputs)
        #self.value = None
        self.separator = ","
        self.file = ""
        self.setDirty()
        self.can_read = True


    def initInnerClasses(self):
        self.content = FileInputContent(self)
        self.grNode  = FileInputGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.openFile.clicked.connect(self.openInputFile)
        self.content.openFile.clicked.connect(self.onInputChanged)


    def openInputFile(self):
        file, filter = QFileDialog.getOpenFileName(self.scene.getView(), 'Open Node-Tree from File')

        if file == '':
            return
        if os.path.isfile(file):
            self.file = file
            self.content.edit.setText(os.path.basename(self.file))
            self.readDFFile(self.file)
        else:
            self.outputs[0].value = "NaN"
            self.outputs[0].type  = 'none'
            self.can_read = False


    def readDFFile(self, file):
        try:
            self.outputs[0].value = pd.read_csv(file, sep=self.separator)
            self.outputs[0].type  = 'df'
            self.can_read = True
        except Exception as e : 
            dumpException(e)
            self.outputs[0].value = "NaN"
            self.outputs[0].type  = 'none'
            self.can_read = False


    def evalImplementation(self):
        if self.can_read : return True
        else: return False
