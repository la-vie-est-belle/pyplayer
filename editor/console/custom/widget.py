import os
import logging
import platform
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.console.custom.menu import LogListViewMenu

print()

"""
日志输出到文件中
"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logFile = Path(__file__).parent.parent / "log" / "console.log"
logFile.touch()

fileHandler = logging.FileHandler(logFile, mode="a")
fileHandler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


class LogListView(QListView):
    def __init__(self):
        super(LogListView, self).__init__()
        self._logList = []
        self._contextMenu = LogListViewMenu()
        self._stringListModel = QStringListModel()
        self._clipboard = QApplication.clipboard()
        self._stringListModel.setStringList(self._logList)

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setAlternatingRowColors(True)
        self.setModel(self._stringListModel)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _setSignal(self):
        self._contextMenu.copySignal.connect(self._copy)
        self._contextMenu.clearSignal.connect(self.clear)

    def _append(self, log):
        self._logList.append(log)
        self._stringListModel.setStringList(self._logList)
        self.scrollToBottom()

    def appendInfo(self, info):
        self._append(f'[INFO] {info}')
        logger.info(info)

    def appendError(self, error):
        self._append(f'[ERROR] {error}')
        logger.error(error)

    def appendWarning(self, warning):
        self._append(f'[WARN] {warning}')
        logger.warning(warning)

    def _copy(self):
        if not self.currentIndex():
            return

        indexData = self.currentIndex().data()
        mimeData = QMimeData()
        mimeData.setText(indexData)
        self._clipboard.setMimeData(mimeData)

    def clear(self):
        self._logList.clear()
        self._stringListModel.setStringList(self._logList)

    def getLog(self):
        return self._logList

    def contextMenuEvent(self, event):
        super(LogListView, self).contextMenuEvent(event)
        self._contextMenu.exec(event.globalPos())


class SearchLine(QLineEdit):
    def __init__(self):
        super(SearchLine, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setPlaceholderText("搜索关键词")
        self.setObjectName("consoleSearchLine")
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

    def _setSignal(self):
        ...

    def contextMenuEvent(self, event):
        pass


class SearchListView(QListView):
    def __init__(self):
        super(SearchListView, self).__init__()
        self._stringListModel = QStringListModel()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.hide()
        self.setAlternatingRowColors(True)
        self.setModel(self._stringListModel)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setResult(self, matchList):
        self._stringListModel.setStringList(matchList)

    def clear(self):
        self._stringListModel.setStringList([])


class ClearButton(QPushButton):
    def __init__(self):
        super(ClearButton, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setObjectName("consoleClearButton")

    def _setSignal(self):
        ...


class OpenLogButton(QPushButton):
    def __init__(self):
        super(OpenLogButton, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setObjectName("consoleLogButton")

    def _setSignal(self):
        system = platform.system()
        if system == "Darwin":
            self.clicked.connect(lambda: os.system(f"open -t {logFile}"))
        elif system == "Windows":
            self.clicked.connect(lambda: os.system(f"notepad {logFile}"))


class LogLevelComboBox(QComboBox):
    def __init__(self):
        super(LogLevelComboBox, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.addItems(["ALL", "INFO", "ERROR", "WARNING"])
