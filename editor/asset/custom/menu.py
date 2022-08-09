from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ProjectTreeViewMenu(QObject):
    # 菜单命令信号
    newFileSignal = pyqtSignal(str)
    newFolderSignal = pyqtSignal()
    openFileSignal = pyqtSignal()
    renameSignal = pyqtSignal()
    deleteSignal = pyqtSignal()
    pasteSignal = pyqtSignal()
    copySignal = pyqtSignal()
    cutSignal = pyqtSignal()

    def __init__(self):
        super(ProjectTreeViewMenu, self).__init__()
        self._clipboard = QApplication.clipboard()

        # 主菜单和子菜单
        self._fileMainMenu = QMenu()
        self._folderMainMenu = QMenu()
        self._blankAreaMainMenu = QMenu()
        self._newFileSubmenu = QMenu("新建文件")

        # 主菜单命令
        self._newFolderAction = QAction("新建文件夹", self)
        self._openFileAction = QAction("打开文件", self)
        self._renameAction = QAction("重命名", self)
        self._deleteAction = QAction("删除", self)
        self._pasteAction = QAction("粘贴", self)
        self._copyAction = QAction("复制", self)
        self._cutAction = QAction("剪切", self)

        # 子菜单命令
        self._newPyFileAction = QAction("新建py文件", self)
        self._newTxtFileAction = QAction("新建txt文件", self)
        self._newJsonFileAction = QAction("新建json文件", self)

        self._setMenu()

    def _setMenu(self):
        self._setSignal()
        self._setAction()

    def _setSignal(self):
        self._newFolderAction.triggered.connect(self.newFolderSignal.emit)
        self._openFileAction.triggered.connect(self.openFileSignal.emit)
        self._renameAction.triggered.connect(self.renameSignal.emit)
        self._deleteAction.triggered.connect(self.deleteSignal.emit)
        self._pasteAction.triggered.connect(self.pasteSignal.emit)
        self._copyAction.triggered.connect(self.copySignal.emit)
        self._cutAction.triggered.connect(self.cutSignal.emit)

        self._newPyFileAction.triggered.connect(lambda: self.newFileSignal.emit(".py"))
        self._newTxtFileAction.triggered.connect(lambda: self.newFileSignal.emit(".txt"))
        self._newJsonFileAction.triggered.connect(lambda: self.newFileSignal.emit(".json"))

    def _setAction(self):
        self._setSubMenuAction()
        self._setFileMainMenuAction()
        self._setFolderMainMenuAction()
        self._setBlankAreaMainMenuAction()

    def _setSubMenuAction(self):
        self._newFileSubmenu.addAction(self._newPyFileAction)
        self._newFileSubmenu.addAction(self._newTxtFileAction)
        self._newFileSubmenu.addAction(self._newJsonFileAction)

    def _setFileMainMenuAction(self):
        self._fileMainMenu.addMenu(self._newFileSubmenu)

        self._fileMainMenu.addAction(self._newFolderAction)
        self._fileMainMenu.addAction(self._openFileAction)
        self._fileMainMenu.addAction(self._renameAction)
        self._fileMainMenu.addAction(self._deleteAction)
        self._fileMainMenu.addAction(self._pasteAction)
        self._fileMainMenu.addAction(self._copyAction)
        self._fileMainMenu.addAction(self._cutAction)

    def _setFolderMainMenuAction(self):
        self._folderMainMenu.addMenu(self._newFileSubmenu)

        self._folderMainMenu.addAction(self._newFolderAction)
        self._folderMainMenu.addAction(self._renameAction)
        self._folderMainMenu.addAction(self._deleteAction)
        self._folderMainMenu.addAction(self._pasteAction)
        self._folderMainMenu.addAction(self._copyAction)
        self._folderMainMenu.addAction(self._cutAction)

    def _setBlankAreaMainMenuAction(self):
        self._blankAreaMainMenu.addMenu(self._newFileSubmenu)

        self._blankAreaMainMenu.addAction(self._newFolderAction)
        self._blankAreaMainMenu.addAction(self._pasteAction)

    def execFileMainMenu(self, pos):
        self._pasteAction.setEnabled(bool(self._clipboard.text()))
        self._fileMainMenu.exec(pos)

    def execFolderMainMenu(self, pos):
        self._pasteAction.setEnabled(bool(self._clipboard.text()))
        self._folderMainMenu.exec(pos)

    def execBlankAreaMainMenu(self, pos):
        self._pasteAction.setEnabled(bool(self._clipboard.text()))
        self._blankAreaMainMenu.exec(pos)
