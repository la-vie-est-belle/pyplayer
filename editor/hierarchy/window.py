import re
import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.hierarchy.custom.widget import ItemTreeView, SearchLine, SearchListView, SearchComboBox


class HierarchyWindow(QWidget):
    cutItemSignal = pyqtSignal(list)
    rootItemSignal = pyqtSignal(str)
    copyItemSignal = pyqtSignal(list)
    deleteItemSignal = pyqtSignal(list)
    newItemSignal = pyqtSignal(str, str, str)
    selectionChangedSignal = pyqtSignal(list)

    def __init__(self):
        super(HierarchyWindow, self).__init__()
        self._searchLine = SearchLine()
        self._itemTreeView = ItemTreeView()
        self._searchListView = SearchListView()
        self._searchComboBox = SearchComboBox()

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
        self._searchListView.doubleClicked.connect(self._locate)

        # 发不出去，暂时先不管Window的uuid
        # self._itemTreeView.rootItemUUIDSignal.connect(self.rootItemSignal.emit)
        self._itemTreeView.cutItemSignal.connect(self.cutItemSignal.emit)
        self._itemTreeView.newItemSignal.connect(self.newItemSignal.emit)
        self._itemTreeView.copyItemSignal.connect(self.copyItemSignal.emit)
        self._itemTreeView.deleteItemSignal.connect(self.deleteItemSignal.emit)
        self._itemTreeView.selectionChangedSignal.connect(self.selectionChangedSignal.emit)

    def _setLayout(self):
        hLayout = QHBoxLayout()
        vLayout = QVBoxLayout(self)
        hLayout.addWidget(self._searchComboBox)
        hLayout.addWidget(self._searchLine)
        hLayout.setContentsMargins(0, 0, 0, 0)
        hLayout.setSpacing(0)
        vLayout.setSpacing(0)
        vLayout.addLayout(hLayout)
        vLayout.addWidget(self._itemTreeView)
        vLayout.addWidget(self._searchListView)
        vLayout.setContentsMargins(0, 0, 0, 0)

    def selectItems(self, selectedUUIDList):
        self._itemTreeView.clearSelection()
        for index in self._itemTreeView.getAllIndexes():
            if index.model().itemFromIndex(index).uuid in selectedUUIDList:
                self._itemTreeView.selectionModel().select(index, QItemSelectionModel.Select)

    def _search(self, keyword):
        if not keyword:
            self._searchListView.hide()
            self._itemTreeView.show()
            return

        matchList = []
        indexDict = self._itemTreeView.getAllIndexes()
        searchComboBoxText = self._searchComboBox.currentText()

        # 如果是按照名称搜索，则匹配节点名称
        # 如果是按照UUID搜索，则匹配UUID
        for index in indexDict.keys():
            if searchComboBoxText == "名称":
                targetText = index.data()
            else:
                targetText = index.model().itemFromIndex(index).uuid

            if re.search(keyword, targetText, re.IGNORECASE):
                matchList.append(index)

        self._searchListView.setResult(matchList, searchComboBoxText)
        self._searchListView.show()
        self._itemTreeView.hide()

    def _locate(self, listViewIndex):
        """
        1. 在层级管理器中定位
        2. 在场景管理器中定位
        """
        self._locateInHierarchy(listViewIndex)

    def _locateInHierarchy(self, listViewIndex):
        listViewItemUUID = listViewIndex.model().itemFromIndex(listViewIndex).uuid
        indexDict = self._itemTreeView.getAllItems()
        for treeViewIndex in indexDict.keys():
            treeViewItemUUID = treeViewIndex.model().itemFromIndex(treeViewIndex).uuid
            if listViewItemUUID == treeViewItemUUID:
                self._itemTreeView.locate(treeViewIndex)
                self._searchListView.hide()
                self._itemTreeView.show()


if __name__ == "__main__":
    app = QApplication([])
    window = HierarchyWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())
