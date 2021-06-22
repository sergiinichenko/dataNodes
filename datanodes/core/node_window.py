
from datanodes.core.node_widget import NodeWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, json

class NodeWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None

        self.initUI()


    def initUI(self):
        nodeEditor = NodeWidget(self)
        self.setCentralWidget(nodeEditor)

        menubar = self.menuBar()

        # Initialize menu
        filemenu = menubar.addMenu('&File')

        # add the New menu
        filemenu.addAction(self.createAct('&New', 'Ctrl+N', 'Create new node tree', self.onFileNew))
        filemenu.addSeparator()
        filemenu.addAction(self.createAct('&Open', 'Ctrl+O', 'Open File', self.onFileOpen))
        filemenu.addAction(self.createAct('&Save', 'Ctrl+S', 'Save File', self.onFileSave))
        filemenu.addAction(self.createAct('Save &As ..', 'Ctrl+Shift+S', 'Save File as ...', self.onFileSaveAs))
        filemenu.addSeparator()
        filemenu.addAction(self.createAct('E&xit', 'Ctrl+Q', 'Exit the application', self.close))


        # Initialize menu
        editmenu = menubar.addMenu('&Edit')

        # add the New menu
        editmenu.addAction(self.createAct('&Undo',  'Ctrl+Z', 'Undo the last operation', self.onEditUndo))
        editmenu.addAction(self.createAct('&Redu',  'Ctrl+Shift+Z', 'Redu the last operation', self.onEditRedo))
        editmenu.addSeparator()
        editmenu.addAction(self.createAct('&Copy',  'Ctrl+C', 'Copy the Item(s)',  self.onEditCopy))
        editmenu.addAction(self.createAct('Cu&t',   'Ctrl+X', 'Cut the Item(s)',   self.onEditCut))
        editmenu.addAction(self.createAct('&Paste', 'Ctrl+V', 'Paste the Item(s)', self.onEditPaste))
        #editmenu.addAction(self.createAct('&Dublicate', 'Ctrl+D', 'Dublicate the Item(s)', self.onEditDublicate))
        editmenu.addSeparator()
        editmenu.addAction(self.createAct('&Delete','Del', 'Delete selected Item(s)', self.onEditDelete))

        # Initialize the status bar
        self.statusBar().showMessage('')
        self.statusMousePosition = QLabel('')
        self.statusBar().addPermanentWidget(self.statusMousePosition)

        nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)

        # Define the window properties
        self.setGeometry(200, 100, 1000, 800)

        self.setWindowTitle("DataNodes")
        self.changeTitle()

        nodeEditor.scene.addHasBeenModifiedListener(self.changeTitle)

        self.show()

    def changeTitle(self):
        title = "DataNodes - "
        if self.filename is None:
            title += "New"
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += "*"

        self.setWindowTitle(title)

    def createAct(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def closeEvent(self, event):
        if self.savePrompt():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.centralWidget().scene.has_been_modified

    def savePrompt(self):
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
        if self.savePrompt():
            self.centralWidget().scene.clear()
            self.filename = None
            self.changeTitle()


    def onFileOpen(self):
        if self.savePrompt():
            file, filter = QFileDialog.getOpenFileName(self, 'Open Node-Tree from File')

            if file == '':
                return
            if os.path.isfile(file):
                self.centralWidget().scene.loadFromFile(file)
                self.filename = file
                self.changeTitle()


    def onFileSave(self):
        if self.filename is None: return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage('Successfully saved as {0}'.format(self.filename))
        self.changeTitle()
        return True

    def onFileSaveAs(self):
        file, filter = QFileDialog.getSaveFileName(self, 'Save Node-Tree to File')

        if file == '':
            return False
        self.filename = file
        self.changeTitle()
        self.onFileSave()
        return True

    def onEditUndo(self):
        self.centralWidget().scene.history.undo()

    def onEditRedo(self):
        self.centralWidget().scene.history.redo()

    def onEditDelete(self):
        self.centralWidget().scene.grScene.views()[0].deleteSelectedItem()



    def onEditCopy(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)


    def onEditCut(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
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

        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)

    def onEditDublicate(self):
        pass