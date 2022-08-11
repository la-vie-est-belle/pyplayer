import re
import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.hierarchy.custom.widget import ItemTreeView, SearchLine, SearchListView


class HierarchyWindow(QWidget):
    def __init__(self):
        super(HierarchyWindow, self).__init__()
        self._searchLine = SearchLine()
        self._itemTreeView = ItemTreeView()
        self._searchListView = SearchListView()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(200, 500)
        self.setWindowTitle("层级管理器")

    def _setSignal(self):
        self._searchLine.textChanged.connect(self._search)

    def _setLayout(self):
        vLayout = QVBoxLayout(self)
        vLayout.setSpacing(3)
        vLayout.addWidget(self._searchLine)
        vLayout.addWidget(self._itemTreeView)
        vLayout.addWidget(self._searchListView)
        vLayout.setContentsMargins(0, 3, 0, 0)

    def _search(self, keyword):
        if not keyword:
            self._searchListView.hide()
            self._itemTreeView.show()
            return

        self._searchListView.show()
        self._itemTreeView.hide()


if __name__ == "__main__":
    app = QApplication([])
    window = HierarchyWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())
