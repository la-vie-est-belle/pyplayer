from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class LogListViewMenu(QObject):
    copySignal = pyqtSignal()
    clearSignal = pyqtSignal()

    def __init__(self):
        super(LogListViewMenu, self).__init__()
        self._clipboard = QApplication.clipboard()
        self._menu = QMenu()

        self._copyAction = QAction("复制", self)
        self._clearAction = QAction("清空", self)

        self._setMenu()

    def _setMenu(self):
        self._setSignal()
        self._setAction()

    def _setSignal(self):
        self._copyAction.triggered.connect(self.copySignal.emit)
        self._clearAction.triggered.connect(self.clearSignal.emit)

    def _setAction(self):
        self._menu.addAction(self._copyAction)
        self._menu.addAction(self._clearAction)

    def exec(self, pos):
        self._menu.exec(pos)