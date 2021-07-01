from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *


class FileInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 140.0
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
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_FILEINPUT)
class FileInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_FILEINPUT
    op_title = "File input"


    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs, outputs)
        self.eval()
        self.value = "File name"


    def initInnerClasses(self):
        self.content = FileInputContent(self)
        self.grNode  = FileInputGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.openFile.clicked.connect(self.openInputFile)

    def openInputFile(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open Node trees form file(s)')

        try:
            for fname in fnames:
                if fname:
                    # read the file logic here
                    with open(fname, "r") as file:
                        raw = file.read()
                        try:
                            data = json.loads(raw, encoding="utf-8")
                            self.deserialize(data)
                            self.has_been_modified = False

                        except json.JSONDecodeError:
                            raise InvalidFile("{0} is not valid json file".format(os.path.basename(filename)))

                        except Exception as e : 
                            dumpException(e)

    def evalImplementation(self):
        try:
            u_value = self.content.edit.text()
            s_value = float(u_value)
            self.value = s_value      
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            
            return False
