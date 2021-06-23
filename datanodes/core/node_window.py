
from datanodes.core.node_widget import NodeWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, json
from datanodes.core.utils import *

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
        self.setCentralWidget(self.nodeEditor)
        self.nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)
        self.nodeEditor.scene.addHasBeenModifiedListener(self.setTitle)

        # Define the window properties
        self.setGeometry(200, 100, 1000, 800)

        self.setWindowTitle("DataNodes")
        self.setTitle()


        self.show()

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setAcriveSubWindow(window)


    def createActions(self):
        self.actNew       = QAction('&New',     self, shortcut='Ctrl+N', statusTip='Create new node tree', triggered=self.onFileNew)
        self.actOpen      = QAction('&Open',    self, shortcut='Ctrl+O', statusTip='Open File',  triggered=self.onFileOpen)
        self.actSave      = QAction('&Save',    self, shortcut='Ctrl+S', statusTip='Save File',  triggered=self.onFileSave)
        self.actSaveAs    = QAction('Save &As', self, shortcut='Ctrl+Shift+S', statusTip='Save File as ...',  triggered=self.onFileSaveAs)
        self.actExit      = QAction('E&xit',    self, shortcut='Ctrl+Q', statusTip='Exit the application',    triggered=self.close)
        self.actUndo      = QAction('&Undo',    self, shortcut='Ctrl+Z', statusTip='Undo the last operation',  triggered=self.onEditUndo)
        self.actRedo      = QAction('&Redu',    self, shortcut='Ctrl+Shift+Z', statusTip='Redu the last operation',  triggered=self.onEditRedo)
        self.actCopy      = QAction('&Copy',    self, shortcut='Ctrl+C', statusTip='Copy the Item(s)',   triggered=self.onEditCopy)
        self.actCut       = QAction('Cu&t',     self, shortcut='Ctrl+X', statusTip='Cut the Item(s)',    triggered=self.onEditCut)
        self.actPaste     = QAction('&Paste',   self, shortcut='Ctrl+V', statusTip='Paste the Item(s)',  triggered=self.onEditPaste)
        self.actDel       = QAction('&Delete',  self, shortcut='Del',    statusTip='Delete selected Item(s)',  triggered=self.onEditDelete)

        self.actClose     = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll  = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile      = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade   = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext      = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious  = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)


    def createMenus(self):
        # Initialize FILE menu
        self.menubar = self.menuBar()
        self.filemenu = self.menubar.addMenu('&File')
        # add the New menu
        self.filemenu.addAction(self.actNew)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.actOpen)
        self.filemenu.addAction(self.actSave)
        self.filemenu.addAction(self.actSaveAs)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.actExit)

        # Initialize EDIT menu
        self.editmenu = self.menubar.addMenu('&Edit')
        # add the New menu
        self.editmenu.addAction(self.actUndo)
        self.editmenu.addAction(self.actRedo)
        self.editmenu.addSeparator()
        self.editmenu.addAction(self.actCopy)
        self.editmenu.addAction(self.actCut)
        self.editmenu.addAction(self.actPaste)
        self.editmenu.addSeparator()
        self.editmenu.addAction(self.actDel)

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
        title += self.getCurrentNodeEditorWidget().getUserFiendlyFilename()

        if self.getCurrentNodeEditorWidget().isModified():
            title += "*"

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
        return nodeeditor.scene.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self):
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
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().scene.clear()
            self.nodeEditor.filename = None
            self.setTitle()

    def onFileOpen(self):
        if self.maybeSave():
            file, filter = QFileDialog.getOpenFileName(self, 'Open Node-Tree from File')

            if file == '':
                return
            if os.path.isfile(file):
                self.getCurrentNodeEditorWidget().scene.loadFromFile(file)
                self.nodeEditor.filename = file
                self.setTitle()

    def onFileSave(self):
        if self.nodeEditor.filename is None: return self.onFileSaveAs()
        self.getCurrentNodeEditorWidget().scene.saveToFile(self.nodeEditor.filename)
        self.statusBar().showMessage('Successfully saved as {0}'.format(self.nodeEditor.filename))
        self.setTitle()
        return True

    def onFileSaveAs(self):
        file, filter = QFileDialog.getSaveFileName(self, 'Save Node-Tree to File')

        if file == '':
            return False
        self.nodeEditor.filename = file
        self.setTitle()
        self.onFileSave()
        return True

    def onEditUndo(self):
        self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        self.getCurrentNodeEditorWidget().scene.grScene.views()[0].deleteSelectedItem()

    def onEditCopy(self):
        data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCut(self):
        data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
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
        
        self.setTitle()

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())
