
from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *


class ValueInputGraphicsNode(DataGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 120.0
        self.height = 90.0

class ValueInputContent(DataContent):
    def initUI(self):
        super().initUI()
  
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(0,0,0,0)

        self.hlayout = QHBoxLayout()
        self.vlayout = QHBoxLayout()
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addLayout(self.vlayout)

        self.label_name = QLabel("", self)        
        self.label_name.setAlignment(Qt.AlignRight)

        self.label = QLineEdit("x", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(60)
        self.hlayout.addWidget(self.label_name)
        self.hlayout.addWidget(self.label)


        self.value = QLineEdit("1.0", self)
        self.value.setAlignment(Qt.AlignCenter)
        self.vlayout.addWidget(self.value)

        self.setLayout(self.mainlayout)


    def serialize(self):
        res = super().serialize()
        res['value'] = self.value.text()
        res['label'] = self.label.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            self.value.setText(data['value'])
            self.label.setText(data['label'])
            return True & res
        except Exception as e : dumpException(e)
        return res

@register_node(OP_MODE_VALINPUT)
class ValueInputNode(DataNode):
    icon = "icons/valinput.png"
    op_code = OP_MODE_VALINPUT
    op_title = "Input value"

    def __init__(self, scene, inputs=[], outputs=[2]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()

    def initSettings(self):
        super().initSettings()
        self.output_socket_position = RIGHT_TOP

    def initInnerClasses(self):
        self.content = ValueInputContent(self)
        self.grNode  = ValueInputGraphicsNode(self)
        self.content.value.textChanged.connect(self.onInputChanged)
        self.content.label.textChanged.connect(self.onInputChanged)
    
    def evalImplementation(self):
        try:
            u_value = self.content.value.text()
            s_value = float(u_value)
            label   = self.content.label.text()
            self.getOutput(0).value = {label : s_value}
            self.getOutput(0).type  = "float"
            return True

        except Exception as e: 
            dumpException (e)
            self.e = e
            
            return False
