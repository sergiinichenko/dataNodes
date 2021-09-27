from datanodes.graphics.graphics_view import MODE_EDGE_DRAG
from datanodes.core.node_edge import EDGE_BEZIER, EDGE_DIRECT
from datanodes.core.node_widget import NodeWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, json
from datanodes.core.utils import *
from datanodes.core.main_conf import *
from datanodes.core.node_node import *
from datanodes.nodes.datanode import *

DEBUG = False

class NodeWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.name_company = "SergiiCompany"
        self.name_product = "DataNodes editor"

        self.initUI()


    def initUI(self):

        self.createActions()
        self.createMenus()
        self.createStatusBar()

        self.readSettings()

        self.setWindowTitle("DataNodes Editor")

        self.createStatusBar()

        self.nodeEditor = NodeWidget(self)
        self.nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)
        self.nodeEditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeEditor)

        # Define the window properties
        self.setGeometry(200, 100, 1000, 800)

        self.setWindowTitle("DataNodes")
        self.setTitle()


        self.show()

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setAcriveSubWindow(window)


    def createActions(self):
        self.actNew       = QAction('&New',     self, shortcut=QKeySequence('Ctrl+N'), statusTip='Create new node tree', triggered=self.onFileNew)
        self.actOpen      = QAction('&Open',    self, shortcut=QKeySequence('Ctrl+O'), statusTip='Open File',  triggered=self.onFileOpen)
        self.actSave      = QAction('&Save',    self, shortcut=QKeySequence('Ctrl+S'), statusTip='Save File',  triggered=self.onFileSave)
        self.actSaveAs    = QAction('Save &As', self, shortcut=QKeySequence('Ctrl+Shift+S'), statusTip='Save File as ...',  triggered=self.onFileSaveAs)
        self.actExit      = QAction('E&xit',    self, shortcut=QKeySequence('Ctrl+Q'), statusTip='Exit the application',    triggered=self.close)
        self.actUndo      = QAction('&Undo',    self, shortcut=QKeySequence('Ctrl+Z'), statusTip='Undo the last operation',  triggered=self.onEditUndo)
        self.actRedo      = QAction('&Redu',    self, shortcut=QKeySequence('Ctrl+Shift+Z'), statusTip='Redu the last operation',  triggered=self.onEditRedo)
        self.actCopy      = QAction('&Copy',    self, shortcut=QKeySequence('Ctrl+C'), statusTip='Copy the Item(s)',   triggered=self.onEditCopy)
        self.actCut       = QAction('Cu&t',     self, shortcut=QKeySequence('Ctrl+X'), statusTip='Cut the Item(s)',    triggered=self.onEditCut)
        self.actPaste     = QAction('&Paste',   self, shortcut=QKeySequence('Ctrl+V'), statusTip='Paste the Item(s)',  triggered=self.onEditPaste)
        self.actDublicate = QAction('Du&blicate',   self, shortcut=QKeySequence('Ctrl+D'), statusTip='Dublicate the Item(s)',  triggered=self.onEditDublicate)
        self.actDel       = QAction('&Delete',  self, shortcut=QKeySequence(Qt.Key_Delete),    statusTip='Delete selected Item(s)',  triggered=self.onEditDelete)
        self.actDelX      = QAction('Del&X',    self, shortcut=QKeySequence(Qt.Key_X),      statusTip='Delete selected Item(s)',  triggered=self.onEditDelete)
        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

    def createMenus(self):
        # Initialize FILE menu
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&File')
        # add the New menu
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

        # Initialize EDIT menu
        self.editMenu = self.menubar.addMenu('&Edit')
        # add the New menu
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addAction(self.actDublicate)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDel)

    def createStatusBar(self):
        self.statusBar().showMessage('Ready ...')
        self.statusMousePosition = QLabel('')
        self.statusBar().addPermanentWidget(self.statusMousePosition)

    def readSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos      = settings.value('pos',  QPoint(200, 200))
        size     = settings.value('size', QSize(1000, 800))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos',  self.pos())
        settings.setValue('size', self.size())

    def setTitle(self):
        title  = "DataNodes - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)


    def closeEvent(self, event):
        """Handle close event. Ask before we loose work"""
        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()



    def isModified(self):
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self) -> NodeWidget:
        """get current :class:`~nodeeditor.node_editor_widget`

        :return: get current :class:`~nodeeditor.node_editor_widget`
        :rtype: :class:`~nodeeditor.node_editor_widget`
        """
        return self.centralWidget()


    def maybeSave(self):
        if not self.isModified():
            return True
        
        res = QMessageBox.warning(self, "Save before closing",
            "The file has been modified. \n Do you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if res == QMessageBox.Save:
            return self.onFileSave()

        elif res == QMessageBox.Cancel:
            return False
        
        else:
            return True


    def onScenePosChanged(self, x, y):
        self.statusMousePosition.setText("Scene Pos: {0} {1}".format(x, y))


    def onFileNew(self):
        """Hande File New operation"""
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()

    def onFileOpen(self):
        if self.maybeSave():
            file, filter = QFileDialog.getOpenFileName(self, 'Open Node-Tree from File')

            if file == '':
                return
            if os.path.isfile(file):
                self.getCurrentNodeEditorWidget().fileLoad(file)
                self.setTitle()


    def onFileSave(self):
        current_editor = self.getCurrentNodeEditorWidget()
        if current_editor is None : return

        if not current_editor.isFilenameSet(): return self.onFileSaveAs()
        current_editor.fileSave()

        self.statusBar().showMessage('Successfully saved as {0}'.format(current_editor.filename), 5000)
        if hasattr(current_editor, 'setTitle') : current_editor.setTitle()
        else : self.setTitle()
        return True

    def onFileSaveAs(self):
        current_editor = self.getCurrentNodeEditorWidget()
        if current_editor is None : return

        file, filter = QFileDialog.getSaveFileName(self, 'Save Node-Tree to File')
        if file == '' : return False

        current_editor.fileSave(file)

        self.statusBar().showMessage('Successfully saved as {0}'.format(current_editor.filename), 5000)
        if hasattr(current_editor, 'setTitle') : current_editor.setTitle()
        else : self.setTitle()

        return True


    def onEditUndo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelectedItem()

    def onEditCopy(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCut(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self, setSelected=False):
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()
            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Paste not valid json data: ", e)
                return

            # Check if the data is correct
            if 'nodes' not in data:
                print('JSON does not contain any nodes')
                return

            self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data, setSelected)

    def onEditDublicate(self):
        self.onEditCopy()
        self.getCurrentNodeEditorWidget().scene.deselectAll()
        self.onEditPaste(setSelected=True)




class NodeSubWindow(NodeWidget):
    def __init__(self, window):
        super().__init__(window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        
        self.setTitle()
        self.initNewNodeActions()

        self.scene.setNodeClassSelector(self.getNodeClassFromData)
        self._close_event_listener = []

    def getNodeClassFromData(self, data):
        if 'op_code' not in data : return Node
        return getClassFromOpCode(data['op_code'])

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(DATA_NODES.keys())
        keys.sort()
        for key in keys : 
            node = DATA_NODES[key]
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def populateSubMenu(self, menu, values=[10, 20]):
        # Step 1. Remove the old options from the menu
        menu.clear()
        # Step 2. Dynamically create the actions
        keys = list(DATA_NODES.keys())
        keys.sort()
        filtered_keys = [number for number in keys if number >= values[0] and number < values[1]]
        for key in filtered_keys : menu.addAction(self.node_actions[key])

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        self.input_menu = context_menu.addMenu("Input")
        self.populateSubMenu(self.input_menu, [100, 200])

        self.output_menu = context_menu.addMenu("Output")
        self.populateSubMenu(self.output_menu, [200, 300])

        self.math_menu = context_menu.addMenu("Math")
        self.populateSubMenu(self.math_menu, [300, 400])

        self.data_menu = context_menu.addMenu("Data process")
        self.populateSubMenu(self.data_menu, [400, 500])

        self.data_menu = context_menu.addMenu("Additional")
        self.populateSubMenu(self.data_menu, [500, 600])

        self.data_menu = context_menu.addMenu("Statistics")
        self.populateSubMenu(self.data_menu, [600, 700])

        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listener.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listener : callback(self, event)
        return super().closeEvent(event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData   = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream  = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap      = QPixmap()
            dataStream  >> pixmap
            op_code     = dataStream.readInt()
            text        = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.getView().mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                #node = DataNode(self.scene, op_code, text, inputs  = [1,1], outputs = [2])
                node = getClassFromOpCode(op_code)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()
    
    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAtPos(event.pos())

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)

            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)

            else:
                self.handleNewNodeContextMenu(event)
                
            return super().contextMenuEvent(event)
        except Exception as e : 
            dumpException(e)


    def handleNodeContextMenu(self, event):
        context_menu = QMenu(self)
        markDirtyAct     = context_menu.addAction("Mark Dirty")
        markDirtyDescAct = context_menu.addAction("Mark Descendants Dirty")
        unmarkDirtyAct   = context_menu.addAction("Unmark Dirty")
        markInvalidAct   = context_menu.addAction("Mark Invalid")
        markInvalidDescAct = context_menu.addAction("Mark Descendants Invalid")
        unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        muteAct          = context_menu.addAction("Mute")
        unmuteAct        = context_menu.addAction("Unmute")
        evalAct          = context_menu.addAction("Eval")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        
        selected = None
        item = self.scene.getItemAtPos(event.pos())
        if type(item) == QGraphicsProxyWidget : item = item.widget()
        if hasattr(item, 'node') : selected   = item.node
        if hasattr(item, 'socket') : selected = item.socket.node

        if selected and action == markDirtyAct : selected.setDirty()
        if selected and action == unmarkDirtyAct : selected.setDirty(False)
        if selected and action == markDirtyDescAct : selected.setDescendentsDirty()
        if selected and action == markInvalidAct : selected.setInvalid()
        if selected and action == markInvalidDescAct : selected.setDescendentsInvalid()
        if selected and action == unmarkInvalidAct : selected.setInvalid(False)
        if selected and action == muteAct : selected.setMute()
        if selected and action == unmuteAct : selected.setMute(False)
        if selected and action == evalAct : selected.eval()

        if selected and action == evalAct:
            val = selected.eval()


    def handleEdgeContextMenu(self, event):
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        
        selected = None
        item = self.scene.getItemAtPos(event.pos())
        if hasattr(item, 'edge') : selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EDGE_BEZIER
        if selected and action == directAct: selected.edge_type = EDGE_DIRECT


    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_node.inputs) > 0: target_socket = new_node.inputs[0]
        else:
            if len(new_node.outputs) > 0: target_socket = new_node.outputs[0]
        return target_socket

    def finish_new_node_state(self, new_node):
        self.scene.deselectAll()
        new_node.grNode.select(True)
        new_node.grNode.onSelected()




    def handleNewNodeContextMenu(self, event):
        context_menu = self.initNodesContextMenu()
        action       = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_data_node = getClassFromOpCode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            
            new_data_node.setPos(scene_pos.x(), scene_pos.y())

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                target_socket = self.determine_target_socket_of_node(self.scene.getView().dragging.drag_start_socket.is_output, new_data_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.grSocket)
                    self.finish_new_node_state(new_data_node)

            else:
                self.scene.history.storeHistory("Created %s" % new_data_node.__class__.__name__)
