from datanodes.core.node_window import NodeWindow, NodeSubWindow
from datanodes.core.node_widget import NodeWidget
from datanodes.core.node_listbox import NodeListBox, NodesDock
from datanodes.core.node_propertiesdock import PropertiesDock
from PyQt5.QtWidgets import QMdiArea, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings, QPoint
from PyQt5.QtGui import QIcon, QKeySequence
import os, json, inspect
from datanodes.core.utils import *
from datanodes.core.main_conf import *

"""
from datanodes.nodes.datanode import *
from datanodes.nodes.inputs import *
from datanodes.nodes.math import *
from datanodes.nodes.outputs import *
"""
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
            os.path.join(os.path.dirname(__file__), "qss/nodestyle-dark.qss"),
            os.path.join(os.path.dirname(__file__), "qss/nodestyle.qss")
        )

        self.empty_icon = QIcon(".")

        self.createNodesDock()
        self.createPropertiesDock()
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.updateMenus()
        self.createStatusBar()
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
        #self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def createToolBars(self):
        pass

    def updateMenus(self):
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.updateEditMenu()


    def updateEditMenu(self):
        try:
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)

            self.actPaste.setEnabled(hasMdiChild)

            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDel.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e : dumpException(e)


    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())
        toolbar_nodes.setShortcut(QKeySequence('N'))

        toolbar_properties = self.windowMenu.addAction("Properties Toolbar")
        toolbar_properties.setCheckable(True)
        toolbar_properties.triggered.connect(self.onWindowPropertiesDock)
        toolbar_properties.setChecked(self.propertiesDock.isVisible())
        toolbar_properties.setShortcut(QKeySequence('P'))

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
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def createNodesDock(self):
        self.nodesDock = NodesDock("Nodes")
        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)


    def onWindowPropertiesDock(self):
        if self.propertiesDock.isVisible():
            self.propertiesDock.hide()
        else:
            self.propertiesDock.show()

    def createPropertiesDock(self):
        self.propertiesDock = PropertiesDock("Propertes")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.propertiesDock)



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
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e: dumpException(e)


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
                        nodeeditor = NodeSubWindow(self)
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage("File {0} loaded".format(fname))
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()

        except Exception as e : dumpException(e)
        

    def createMdiChild(self, childWidget = None):
        nodeeditor = childWidget if childWidget is not None else NodeSubWindow(self)
        subwnd     = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setWindowIcon(self.empty_icon)
        #nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        #nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWindowClose)
        return subwnd

    def onSubWindowClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave() : 
            event.accept()
        else:
            event.ignore()


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

    def getCurrentNodeEditorWidget(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None
