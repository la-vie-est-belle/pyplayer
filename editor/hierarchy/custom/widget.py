import os
import shutil
import platform
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.uitl import getUUID
from editor.hierarchy.custom.menu import ItemTreeViewMenu


class HierarchyItem(QStandardItem):
    def __init__(self, name, uuid=None):
        super(HierarchyItem, self).__init__(name)
        self.uuid = uuid if uuid else getUUID()


class ItemTreeView(QTreeView):
    def __init__(self):
        super(ItemTreeView, self).__init__()
        self._standardItemModel = QStandardItemModel()
        self._clipboard = QApplication.clipboard()
        self._contextMenu = ItemTreeViewMenu()
        self._currentClickedIndex = None

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setHeaderHidden(True)
        self.setModel(self._standardItemModel)
        self.setObjectName("hierarchyItemTreeView")
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        item = QStandardItem('Scene')
        item2 = QStandardItem("Canvas")
        item.setChild(0, item2)
        self._standardItemModel.appendRow(item)

    def _setSignal(self):
        self.doubleClicked.connect(self._locate)
        self._contextMenu.renameSignal.connect(self._rename)
        self._contextMenu.deleteSignal.connect(self._delete)

    def _locate(self, index):
        """定位"""
        ...

    def _rename(self):
        self.edit(self._currentClickedIndex)

    def _delete(self):
        choice = QMessageBox.question(self, '删除', '确定要删除吗？', QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.No:
            return

        itemsToDelete = []
        for index in self.selectedIndexes():
            if index.data() == "Scene":
                QMessageBox.critical(self, '注意', 'Scene根节点无法删除', QMessageBox.Ok)
            else:
                item = self._standardItemModel.itemFromIndex(index)
                itemsToDelete.append(item)

        for item in itemsToDelete:
            try:
                if item.parent():
                    item.parent().removeRow(item.row())
                else:
                    self._standardItemModel.removeRow(item.row())
            except RuntimeError:
                # 父节点删除又删除子节点时会出现RuntimeError
                # 这里通过try-except来解决
                pass

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self._currentClickedIndex = index

        if not index.isValid():
            self._contextMenu.execBlankAreaMainMenu(event.globalPos())
        else:
            self._contextMenu.execItemMainMenu(event.globalPos())

    def mousePressEvent(self, event):
        super(ItemTreeView, self).mousePressEvent(event)
        if not self.indexAt(event.pos()).isValid():
            self._currentClickedIndex = None
            self.clearSelection()


class SearchLine(QLineEdit):
    def __init__(self):
        super(SearchLine, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.setPlaceholderText("搜索项")
        self.setObjectName("hierarchySearchLine")
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

    def contextMenuEvent(self, event):
        pass


class SearchListView(QListView):
    def __init__(self):
        super(SearchListView, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.hide()


