from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ItemTreeViewMenu(QObject):
    newItemSignal = pyqtSignal(str)
    renameSignal = pyqtSignal()
    deleteSignal = pyqtSignal()
    pasteSignal = pyqtSignal()
    copySignal = pyqtSignal()
    cutSignal = pyqtSignal()

    def __init__(self):
        super(ItemTreeViewMenu, self).__init__()
        self._clipboard = QApplication.clipboard()

        # 主菜单和子菜单
        self._itemMainMenu = QMenu()
        self._blankAreaMainMenu = QMenu()
        self._newItemSubmenu = QMenu("创建项")

        # 主菜单命令
        self._renameAction = QAction("重命名", self)
        self._deleteAction = QAction("删除", self)
        self._pasteAction = QAction("粘贴", self)
        self._copyAction = QAction("复制", self)
        self._cutAction = QAction("剪切", self)

        # 子菜单命令
        self._newLabelAction = QAction("Label", self._newItemSubmenu)
        ...

        self._setMenu()

    def _setMenu(self):
        self._setSignal()
        self._setAction()

    def _setSignal(self):
        self._renameAction.triggered.connect(self.renameSignal.emit)
        self._deleteAction.triggered.connect(self.deleteSignal.emit)
        self._pasteAction.triggered.connect(self.pasteSignal.emit)
        self._copyAction.triggered.connect(self.copySignal.emit)
        self._cutAction.triggered.connect(self.cutSignal.emit)

        self._newLabelAction.triggered.connect(lambda: self.newItemSignal.emit("Label"))
        ...

    def _setAction(self):
        self._setSubMenuAction()
        self._setItemMainMenuAction()
        self._setBlankAreaMainMenuAction()

    def _setSubMenuAction(self):
        self._newItemSubmenu.addAction(self._newLabelAction)
        ...

    def _setItemMainMenuAction(self):
        self._itemMainMenu.addMenu(self._newItemSubmenu)
        self._itemMainMenu.addAction(self._renameAction)
        self._itemMainMenu.addAction(self._deleteAction)
        self._itemMainMenu.addAction(self._pasteAction)
        self._itemMainMenu.addAction(self._copyAction)
        self._itemMainMenu.addAction(self._cutAction)

    def _setBlankAreaMainMenuAction(self):
        self._blankAreaMainMenu.addMenu(self._newItemSubmenu)
        self._blankAreaMainMenu.addAction(self._pasteAction)

    def execItemMainMenu(self, pos):
        # self._pasteAction.setEnabled(bool(self._clipboard.text()))
        self._itemMainMenu.exec(pos)

    def execBlankAreaMainMenu(self, pos):
        # self._pasteAction.setEnabled(bool(self._clipboard.text()))
        self._blankAreaMainMenu.exec(pos)
