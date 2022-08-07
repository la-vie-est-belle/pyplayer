import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from custom.widget import ProjectTreeView, SearchLine


class AssetWindow(QWidget):
    def __init__(self):
        super(AssetWindow, self).__init__()
        self._searchLine = SearchLine()
        self._projectTreeView = ProjectTreeView()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(200, 400)
        self.setWindowTitle("资源管理器")

    def _setSignal(self):
        ...

    def _setLayout(self):
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(self._searchLine)
        vLayout.addWidget(self._projectTreeView)
        vLayout.setContentsMargins(0, 0, 0, 0)



if __name__ == "__main__":
    app = QApplication([])
    window = AssetWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    app.exit(app.exec())



