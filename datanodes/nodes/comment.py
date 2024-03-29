from datanodes.core.utils import dumpException
from datanodes.core.main_conf import *
from datanodes.nodes.datanode import *
from PyQt5.QtWidgets import QPlainTextEdit

class CommentGraphicsNode(ResizebleDataNode):
    def initSizes(self):
        super().initSizes()
        self.width  = 300
        self.height = 300

class CommentContent(DataContent):
    def initUI(self):
        super().initUI()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Comment area
        self.comment = QPlainTextEdit()
        self.layout.addWidget(self.comment)

    def serialize(self):
        res = super().serialize()
        res['width'] = self.node.grNode.width
        res['height'] = self.node.grNode.height
        res['comment']        = self.comment.toPlainText()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            try:
                self.node.grNode.height = data['height']
                self.node.grNode.width  = data['width']
                self.updateSize()
                self.comment.insertPlainText(data['comment'])
            except Exception as e: 
                dumpException(e)
            return True & res
        except Exception as e : dumpException(e)
        return res


@register_node(OP_MODE_COMMENT)
class CommentNode(DataNode):
    icon = "icons/valoutput.png"
    op_code = OP_MODE_COMMENT
    op_title = "Comment"

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, inputs, outputs)
        self.setDirty(False)
        self.setInvalid(False)

    def initInnerClasses(self):
        self.content = CommentContent(self)
        self.grNode  = CommentGraphicsNode(self)
        self.properties = NodeProperties(self)

    def evalImplementation(self, silent=False):
        try:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = ""
            return True
        except Exception as e:
            self.setDirty(False)
            self.setInvalid(False)
            self.e = e
            return False
