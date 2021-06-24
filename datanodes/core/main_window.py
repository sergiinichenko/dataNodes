from datanodes.core.node_window import NodeWindow, NodeSubWindow
from datanodes.core.node_widget import NodeWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, json, inspect
from datanodes.core.utils import *


class MainWindow(NodeWindow):

    def initUI(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/datanodes.qss")
        loadStyleSheets(
            os.path.join(os.path.dirname(__file__), "../qss/nodestyle-dark.qss"),
            os.path.join(os.path.dirname(__file__), "../qss/nodestyle.qss")
        )

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.updateMenus()
        self.createStatusBar()

        self.createNodesDock()

        self.readSettings()

        self.setWindowTitle("DataNodes Editor")

        self.show()

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


    def createActions(self):
        super().createActions()

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
        super().createMenus()

        # Initialize WINDOW menu
        self.windowMenu = self.menubar.addMenu('&Window')
        self.updateWindowMenu()        
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)
        # add the New menu
        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)

        # Initialize ABOUT menu
        self.aboutMenu = self.menubar.addMenu('&About')
        # add the New menu
        self.aboutMenu.addAction(self.actAbout)


    def createToolBars(self):
        pass


    def updateMenus(self):
        active = self.activeMdiChild()
        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)


    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        #toolbar_nodes.setChecked(self.nodesDock.isVisible())

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()
            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowNodesToolbar(self):
        pass

    def createNodesDock(self):
        self.listWidget = QListWidget()
        self.listWidget.addItem("Add")
        self.listWidget.addItem("Substract")
        self.listWidget.addItem("Multiply")
        self.listWidget.addItem("Divide")

        self.items = QDockWidget("Nodes")
        self.items.setWidget(self.listWidget)
        self.items.setFloating(False)
        
        self.addDockWidget(Qt.RightDockWidgetArea, self.items)

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

    def about(self):
        QMessageBox.about(self, "About DataNodes",
                "The DataNodes is a package created for a fast"
                "data processing using the nodes system")


    def onFileNew(self):
        subwnd = self.createMdiChild()
        subwnd.show()

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open Node trees form file(s)')

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we create new subWindow for a file and open file
                        nodeeditor = NodeSubWindow()
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage("File {0} loaded".format(fname))
                            nodeeditor.setTitle()
                            subwnd = self.mdiArea.addSubWindow(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()

        except Exception as e : dumpExcepton(e)


    """
        def onFileSave(self, filename=None):
            current_editor = self.getCurrentNodeEditorWidget()

            if current_editor:
                if not current_editor.isFilenameSet():
                    return self.onFileSaveAs()
                else:
                    current_editor.fileSave()
                    current_editor.setTitle()
                    self.statusBar().showMessage("Successfully save as {0}".format(current_editor.filename), 5000)
                    return True

    def onFileSaveAs(self):
        current_editor = self.activeMdiChild()

        if current_editor:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save Node tree')

            if fname == '' : return False

            current_editor.fileSave(fname)
            current_editor.setTitle()
            self.statusBar().showMessage("Successfully save as {0}".format(fname), 5000)
            return True
    """


    def createMdiChild(self):
        nodeeditor = NodeSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)

        return subwnd

    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None


    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            # hacky fix for PyQt 5.14.x
            import sys
            sys.exit(0)


    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None


    def getCurrentNodeEditorWidget(self):
        return self.activeMdiChild()
