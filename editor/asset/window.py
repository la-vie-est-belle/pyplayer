import re
import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from custom.widget import ProjectTreeView, SearchLine, SearchListView


class AssetWindow(QWidget):
    def __init__(self):
        super(AssetWindow, self).__init__()
        self._searchLine = SearchLine()
        self._searchListView = SearchListView()
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
        self._searchLine.textChanged.connect(self._search)

    def _setLayout(self):
        vLayout = QVBoxLayout(self)
        vLayout.setSpacing(3)
        vLayout.addWidget(self._searchLine)
        vLayout.addWidget(self._searchListView)
        vLayout.addWidget(self._projectTreeView)
        vLayout.setContentsMargins(0, 3, 0, 0)

    def _search(self, keyword):
        if not keyword:
            self._searchListView.hide()
            self._projectTreeView.show()
            return

        matchList = []
        filesAndFolders = self._projectTreeView.getFilesAndFolders()
        for f in filesAndFolders:
            if re.search(keyword, f.name, re.IGNORECASE):
                matchList.append(f)
        self._searchListView.setResult(matchList)
        self._searchListView.show()
        self._projectTreeView.hide()


if __name__ == "__main__":
    app = QApplication([])
    window = AssetWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())



