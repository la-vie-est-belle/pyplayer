import re
import sys
from pathlib import Path
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.console.custom.widget import LogListView, SearchLine, SearchListView, ClearButton, OpenLogButton, LogLevelComboBox


class ConsoleWindow(QWidget):
    def __init__(self):
        super(ConsoleWindow, self).__init__()
        self._clearBtn = ClearButton()
        self._searchLine = SearchLine()
        self._logListView = LogListView()
        self._openLogBtn = OpenLogButton()
        self._searchListView = SearchListView()
        self._logLevelComboBox = LogLevelComboBox()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(600, 200)
        self.setWindowTitle("日志窗口")

    def _setSignal(self):
        self._clearBtn.clicked.connect(self._clear)
        self._searchLine.textChanged.connect(self._search)
        self._logLevelComboBox.currentTextChanged.connect(self._search)

    def _setLayout(self):
        widget = QWidget()
        hLayout = QHBoxLayout(widget)
        hLayout.setSpacing(8)
        hLayout.addWidget(self._clearBtn)
        hLayout.addWidget(self._openLogBtn)
        hLayout.addWidget(self._logLevelComboBox)
        hLayout.addWidget(self._searchLine)

        hLayout.setContentsMargins(0, 0, 0, 0)

        allVLayout = QVBoxLayout(self)
        allVLayout.setSpacing(0)
        allVLayout.addWidget(widget)
        allVLayout.addWidget(self._logListView)
        allVLayout.addWidget(self._searchListView)
        allVLayout.setContentsMargins(0, 0, 0, 0)

    def _search(self, keyword):
        if self.sender() == self._searchLine and not keyword or \
           self.sender() == self._logLevelComboBox and keyword == "ALL":
            self._logListView.show()
            self._searchListView.hide()
            return

        matchList = []
        for log in self._logListView.getLog():
            if re.search(keyword, log, re.IGNORECASE):
                matchList.append(log)

        self._logListView.hide()
        self._searchListView.show()
        self._searchListView.setResult(matchList)

    def _clear(self):
        self._searchLine.clear()
        self._logListView.show()
        self._logListView.clear()
        self._searchListView.hide()
        self._searchListView.clear()


if __name__ == "__main__":
    app = QApplication([])
    window = ConsoleWindow()
    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:
        window.setStyleSheet(f.read())
    window.show()
    sys.exit(app.exec())
