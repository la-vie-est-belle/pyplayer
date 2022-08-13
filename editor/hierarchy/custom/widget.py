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
    copyIndexDict = {}
    cutIndexDict = {}

    def __init__(self):
        super(ItemTreeView, self).__init__()
        self._currentClickedIndex = None
        self._contextMenu = ItemTreeViewMenu(self)
        self._standardItemModel = QStandardItemModel()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        item = HierarchyItem('Scene')
        item2 = HierarchyItem("Canvas")
        item.setChild(0, item2)
        self._standardItemModel.appendRow(item)

        self.setDragEnabled(True)
        self.setHeaderHidden(True)
        self.setModel(self._standardItemModel)
        self.setObjectName("hierarchyItemTreeView")
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.expandAll()

    def _setSignal(self):
        # self.clicked.connect(self._showItem)
        # self.doubleClicked.connect(self._locate)
        self._contextMenu.cutSignal.connect(self._cut)
        self._contextMenu.copySignal.connect(self._copy)
        self._contextMenu.pasteSignal.connect(self._paste)
        self._contextMenu.renameSignal.connect(self._rename)
        self._contextMenu.deleteSignal.connect(self._delete)
        self._contextMenu.newItemSignal.connect(self._createNewItem)

    def _showItem(self, index):
        # 在属性窗口中显示属性

        # 在场景管理器中显示选中
        item = self._standardItemModel.itemFromIndex(index)
        print(item.uuid)

    def _locate(self, index):
        """定位"""
        # 在层级管理器中定位
        ...

        # 在场景管理器中定位
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

    def _createNewItem(self, name):
        newItem = HierarchyItem(name)

        if not self._currentClickedIndex.isValid():
            self._standardItemModel.appendRow(newItem)
            return

        self._standardItemModel.itemFromIndex(self._currentClickedIndex).appendRow(newItem)
        self.expand(self._currentClickedIndex)

    def _paste(self):
        if self.cutIndexDict:
            self._pasteForCut()
        elif self.copyIndexDict:
            self._pasteForCopy()

    def _pasteForCut(self):
        if not self._currentClickedIndex.isValid():
            for parentIndex, childIndexList in self.cutIndexDict.items():
                parentItem = HierarchyItem(parentIndex.data(), self._standardItemModel.itemFromIndex(parentIndex).uuid)

                # 检查是否是字典中最顶层的项
                for temp in list(self.cutIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    self._standardItemModel.appendRow(parentItem)

                # 添加子项
                if childIndexList:
                    self._pasteItemForCutRecursively(self.cutIndexDict, childIndexList, parentItem)

        else:
            # 父项不能剪切到它的子项中
            for parentIndex, childIndexList in self.cutIndexDict.items():
                if self._currentClickedIndex in childIndexList:
                    QMessageBox.critical(self, "注意", "父项不能剪切到子项中。", QMessageBox.Yes)
                    return
                elif self._currentClickedIndex == parentIndex:
                    return

            currentClickedItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
            for parentIndex, childIndexList in self.cutIndexDict.items():
                parentItem = HierarchyItem(parentIndex.data(), self._standardItemModel.itemFromIndex(parentIndex).uuid)

                # 检查是否是字典中最顶层的项
                for temp in list(self.cutIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    currentClickedItem.appendRow(parentItem)

                # 添加子项
                if childIndexList:
                    self._pasteItemForCutRecursively(self.cutIndexDict, childIndexList, parentItem)

        itemsToDelete = []
        for index in self.cutIndexDict.keys():
            item = self._standardItemModel.itemFromIndex(index)
            itemsToDelete.append(item)

        #############################################
        # 为什么某个节点有三个子节点时，删除就会导致崩溃？？？#
        #############################################
        for item in itemsToDelete:
            try:
                if item.parent():
                    item.parent().setRowCount(0)
                else:
                    self._standardItemModel.removeRow(item.row())
            except RuntimeError:
                pass

        self.cutIndexDict.clear()

    def _pasteItemForCutRecursively(self, indexDict, childIndexList, parentItem):
        for childIndex in childIndexList:
            childItem = HierarchyItem(childIndex.data(), self._standardItemModel.itemFromIndex(childIndex).uuid)
            parentItem.appendRow(childItem)
            self.expand(self._standardItemModel.indexFromItem(parentItem))
            if indexDict.get(childIndex):
                self._pasteItemForCutRecursively(indexDict, indexDict[childIndex], childItem)

    def _pasteForCopy(self):
        if not self._currentClickedIndex.isValid():
            for parentIndex, childIndexList in self.copyIndexDict.items():
                parentItem = HierarchyItem(parentIndex.data(), self._standardItemModel.itemFromIndex(parentIndex).uuid)

                # 检查是否是字典中最顶层的项
                for temp in list(self.copyIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    self._standardItemModel.appendRow(parentItem)

                # 添加子项
                if childIndexList:
                    self._pasteItemForCopyRecursively(self.copyIndexDict, childIndexList, parentItem)

        else:
            currentClickedItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
            for parentIndex, childIndexList in self.copyIndexDict.items():
                parentItem = HierarchyItem(parentIndex.data())

                # 检查是否是字典中最顶层的项
                for temp in list(self.copyIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    currentClickedItem.appendRow(parentItem)

                # 添加子项
                if childIndexList:
                    self._pasteItemForCopyRecursively(self.copyIndexDict, childIndexList, parentItem)

    def _pasteItemForCopyRecursively(self, indexDict, childIndexList, parentItem):
        for childIndex in childIndexList:
            childItem = HierarchyItem(childIndex.data())
            parentItem.appendRow(childItem)
            if indexDict.get(childIndex):
                self._pasteItemForCutRecursively(indexDict, indexDict[childIndex], childItem)

    def _copy(self):
        self.cutIndexDict.clear()
        self.copyIndexDict.clear()

        for i in self.selectedIndexes():
            for j in self.selectedIndexes():
                if i.parent() == j:
                    break
            else:
                self._getChildItemRecursively(self.copyIndexDict, i)

        self.clearSelection()

    def _cut(self):
        self.cutIndexDict.clear()
        self.copyIndexDict.clear()

        for i in self.selectedIndexes():
            for j in self.selectedIndexes():
                if i.parent() == j:
                    break
            else:
                self._getChildItemRecursively(self.cutIndexDict, i)

        self.clearSelection()

    def _getChildItemRecursively(self, indexDict, index):
        indexDict[index] = []
        parentItem = self._standardItemModel.itemFromIndex(index)

        count = 0
        while True:
            childItem = parentItem.child(count, 0)
            if not childItem:
                break

            childIndex = childItem.index()
            indexDict[index].append(childIndex)
            self._getChildItemRecursively(indexDict, childIndex)
            count += 1

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

    def drawRow(self, painter, option, index):
        """用于实现项被剪切时的效果"""
        super(ItemTreeView, self).drawRow(painter, option, index)
        brush = QBrush(QColor(0, 105, 217, 50))
        pen = QPen(QColor(0, 0, 0, 0))
        painter.setBrush(brush)
        painter.setPen(pen)

        for cutIndex in self.cutIndexDict.keys():
            if index != cutIndex:
                continue

            x = option.rect.x()
            y = option.rect.y()
            width = option.rect.width()
            height = option.rect.height()
            painter.drawRect(x, y, width, height)


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


