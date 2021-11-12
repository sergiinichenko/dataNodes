LISTBOX_MIMETYPE = "application/x-item"

OP_MODE_INPUT     = 100
OP_MODE_FILEINPUT = 101
OP_MODE_VALINPUT  = 102
OP_MODE_MULVALINPUT  = 103

OP_MODE_STEPARR   = 110
OP_MODE_NUMPARR   = 111
OP_MODE_FILLPARR  = 112
OP_MODE_MESH2D    = 120
OP_MODE_MESH3D    = 121
OP_TERNARY_GRID   = 122

OP_MODE_TABLEOUTPUT = 201
OP_MODE_TEXTOUTPUT  = 202


OP_MODE_PLOT          = 250
OP_MODE_PLOT_TERNARY  = 251
OP_MODE_PLOT_HEATMAP  = 252
OP_STAT_CROSSCORRPLOT = 270


OP_MODE_MATH        = 300
OP_MODE_EXPRESSION  = 301
OP_MODE_CODEBLOCK   = 302

OP_MODE_DATA_SEP    = 400
OP_MODE_DATA_COMBXY = 401
OP_MODE_DATA_UPDATE = 403
OP_MODE_DATA_CLEAN  = 404
OP_MODE_DATA_RENAME = 405

OP_MODE_COMMENT     = 500

OP_STAT_DESCRIBE    = 601


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
