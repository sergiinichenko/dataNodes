LISTBOX_MIMETYPE = "application/x-item"

OP_MODE_INPUT     = 10
OP_MODE_FILEINPUT = 11
OP_MODE_VALINPUT  = 12

OP_MODE_VALOUTPUT   = 20
OP_MODE_TABLEOUTPUT = 21
OP_MODE_TEXTOUTPUT  = 22
OP_MODE_GRAPHOUTPUT = 23

OP_MODE_MATH        = 30
OP_MODE_EXPRESSION  = 31

OP_MODE_PROCESS  = 40

OP_MODE_CLEAN = 50
OP_MODE_PLOT  = 60


DATA_NODES = {}

class ConfException(Exception) : pass
class InvalidNodeRegistration(ConfException) : pass
class OpCodeNotRegistered(ConfException): pass


def registerNode(op_code, class_reference):
    if op_code in DATA_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" %(
            op_code, DATA_NODES[op_code]
        ))  
    DATA_NODES[op_code] = class_reference

def register_node(op_code):
    def decorator(originar_class):
        registerNode(op_code, originar_class)
        return originar_class
    return decorator

def getClassFromOpCode(op_code):
    if op_code not in DATA_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return DATA_NODES[op_code]

from datanodes.nodes import *
