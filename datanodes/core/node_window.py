from datanodes.core.node_widget import NodeWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, json
from datanodes.core.utils import *
from datanodes.core.main_conf import *
from datanodes.core.node_node import *

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
        self.actDel       = QAction('&Delete',  self, shortcut=QKeySequence('Del'),    statusTip='Delete selected Item(s)',  triggered=self.onEditDelete)

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
            self.getCurrentNodeEditorWidget().scene.grScene.views()[0].deleteSelectedItem()

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

    def onEditPaste(self):
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

            self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def onEditDublicate(self):
        pass



class NodeSubWindow(NodeWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        
        self.setTitle()

        self._close_event_listener = []

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listener.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listener : callback(self, event)
        return super().closeEvent()


    def onDragEnter(self, event):
        print("On drag enter")
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            print(".... denied drag enter event")
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
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                node = Node(self.scene, text, inputs  = [1,1,1], outputs = [2])
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.addNode(node)
                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()

