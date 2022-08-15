from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.uitl import getUUID
from editor.hierarchy.custom.menu import ItemTreeViewMenu


class HierarchyItem(QStandardItem):
    def __init__(self, name, uuid=None):
        super(HierarchyItem, self).__init__(name)
        self.uuid = uuid if uuid else getUUID()
        self.setToolTip(self.uuid)


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

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setHeaderHidden(True)
        self.setModel(self._standardItemModel)
        self.setObjectName("hierarchyItemTreeView")
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.expandAll()

    def _setSignal(self):
        # self.clicked.connect(self._showItem)
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

    def locate(self, index):
        self.clearSelection()
        self.expand(index.parent())
        self.selectionModel().select(index, QItemSelectionModel.Select)

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

        for item in itemsToDelete:
            try:
                if item.parent():
                    item.parent().removeRow(item.row())
                else:
                    self._standardItemModel.removeRow(item.row())
            except RuntimeError:
                pass

        self.cutIndexDict.clear()

    def _pasteItemForCutRecursively(self, indexDict, childIndexList, parentItem):
        for childIndex in childIndexList:
            childItem = HierarchyItem(childIndex.data(), self._standardItemModel.itemFromIndex(childIndex).uuid)
            parentItem.appendRow(childItem)
            if indexDict.get(childIndex):
                self._pasteItemForCutRecursively(indexDict, indexDict[childIndex], childItem)

    def _pasteForCopy(self):
        if not self._currentClickedIndex.isValid():
            for parentIndex, childIndexList in self.copyIndexDict.items():
                parentItem = HierarchyItem(parentIndex.data())

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

    def getAllItems(self):
        indexDict = {}
        for row in range(self._standardItemModel.rowCount()):
            index = self._standardItemModel.item(row, 0).index()
            self._getChildItemRecursively(indexDict, index)

        return indexDict

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self._currentClickedIndex = index

        if not index.isValid():
            self._contextMenu.execBlankAreaMainMenu(event.globalPos())
        else:
            self._contextMenu.execItemMainMenu(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.accept()

    def dragMoveEvent(self, event):
        ...

    def dropEvent(self, event):
        index = self.indexAt(event.pos())
        self._currentClickedIndex = index

        # 拖放的时候就用剪切的逻辑
        # 应该把之前剪切的内容清空
        # 否则可能会造成混乱（报错）
        self._cut()
        self._pasteForCut()

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


class SearchComboBox(QComboBox):
    def __init__(self):
        super(SearchComboBox, self).__init__()
        self._searchChoice = "名称"
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.addItems(["名称", "UUID"])

    def _setSignal(self):
        self.currentTextChanged.connect(lambda: self.setSearchChoice)

    def setSearchChoice(self, text):
        self._searchChoice = text


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
        self._standardItemModel = QStandardItemModel()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.hide()
        self.setModel(self._standardItemModel)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setResult(self, matchList, searchComboBoxText):
        self._standardItemModel.clear()

        for index in matchList:
            model = index.model()
            item = model.itemFromIndex(index)
            newItem = HierarchyItem(index.data(), item.uuid)

            # 如果是按照名称搜索，则tooltip设置为节点路径信息
            # 如果是按照UUID搜索，则tooltip设置为节点UUID
            toolTip = index.data()
            if searchComboBoxText == "名称":
                while True:
                    if index.parent().data():
                        toolTip = f"{index.parent().data()}/{toolTip}"
                        index = index.parent()
                    else:
                        break
            else:
                toolTip = newItem.uuid

            newItem.setToolTip(toolTip)
            self._standardItemModel.appendRow(newItem)


