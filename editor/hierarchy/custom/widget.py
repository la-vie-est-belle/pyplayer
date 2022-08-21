from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.util import getUUID
from editor.hierarchy.custom.menu import ItemTreeViewMenu


class HierarchyItem(QStandardItem):
    def __init__(self, objectName, itemType, uuid=None):
        super(HierarchyItem, self).__init__(objectName)
        self.itemType = itemType
        self.uuid = uuid if uuid else getUUID()
        self.setToolTip(self.uuid)


class ItemTreeView(QTreeView):
    copyIndexDict = {}
    cutIndexDict = {}

    cutItemSignal = pyqtSignal(list)
    copyItemSignal = pyqtSignal(list)
    deleteItemSignal = pyqtSignal(list)
    rootItemUUIDSignal = pyqtSignal(str)
    selectionChangedSignal = pyqtSignal(list)
    newItemSignal = pyqtSignal(str, str, str)

    def __init__(self):
        super(ItemTreeView, self).__init__()
        self._isRootUUIDSent = False
        self._currentClickedIndex = None
        self._contextMenu = ItemTreeViewMenu(self)
        self._standardItemModel = QStandardItemModel()
        self._rootItem = HierarchyItem("Window", "Root")

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self._rootItem.setSelectable(False)
        self._standardItemModel.appendRow(self._rootItem)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setHeaderHidden(True)
        self.setModel(self._standardItemModel)
        self.setObjectName("hierarchyItemTreeView")
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.expandAll()

    def _setSignal(self):
        self.clicked.connect(self._showItemInSceneAndPropertyWindow)
        self._contextMenu.cutSignal.connect(self._cut)
        self._contextMenu.copySignal.connect(self._copy)
        self._contextMenu.pasteSignal.connect(self._paste)
        self._contextMenu.renameSignal.connect(self._rename)
        self._contextMenu.deleteSignal.connect(self._delete)
        self._contextMenu.newItemSignal.connect(self._createNewItem)

    def _showItemInSceneAndPropertyWindow(self):
        # 在属性窗口中显示属性
        selectedUUIDList = []
        for index in self.selectedIndexes():
            uuid = self._standardItemModel.itemFromIndex(index).uuid
            selectedUUIDList.append(uuid)

        self.selectionChangedSignal.emit(selectedUUIDList)

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
        deletedUUIDList = []
        for index in self.selectedIndexes():
            item = self._standardItemModel.itemFromIndex(index)
            itemsToDelete.append(item)
            deletedUUIDList.append(item.uuid)

            # 当前设计是无法选中Window根节点
            # if index.data() == "Window":
            #     QMessageBox.critical(self, '注意', '窗口节点无法删除', QMessageBox.Ok)
            # else:
            #     item = self._standardItemModel.itemFromIndex(index)
            #     itemsToDelete.append(item)
            #     deletedUUIDList.append(item.uuid)

        self.deleteItemSignal.emit(deletedUUIDList)
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
        newItem = HierarchyItem(name, name)

        if not self._currentClickedIndex.isValid():
            self._standardItemModel.appendRow(newItem)
            return

        parentItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
        parentItem.appendRow(newItem)
        self.expand(self._currentClickedIndex)
        self.newItemSignal.emit(name, newItem.uuid, parentItem.uuid)

    def _paste(self):
        if self.cutIndexDict:
            self._pasteForCut()
        elif self.copyIndexDict:
            self._pasteForCopy()

    def _pasteForCut(self):
        if not self._currentClickedIndex.isValid():
            return
            # for parentIndex, childIndexList in self.cutIndexDict.items():
            #     parentItem = HierarchyItem(parentIndex.data(), self._standardItemModel.itemFromIndex(parentIndex).uuid)
            #
            #     # 检查是否是字典中最顶层的项
            #     for temp in list(self.cutIndexDict.values()):
            #         if parentIndex in temp:
            #             break
            #     else:
            #         self._standardItemModel.appendRow(parentItem)
            #
            #     # 添加子项
            #     if childIndexList:
            #         self._pasteItemForCutRecursively(self.cutIndexDict, childIndexList, parentItem)

        else:
            # 父项不能剪切到它的子项中
            # 剪切到自身节点上的话同样清空剪切内容
            cutItemList = []
            for parentIndex, childIndexList in self.cutIndexDict.items():
                if self._currentClickedIndex in childIndexList:
                    QMessageBox.critical(self, "注意", "父项不能移动到子项中。", QMessageBox.Yes)
                    self.cutIndexDict.clear()
                    return
                elif self._currentClickedIndex == parentIndex:
                    self.cutIndexDict.clear()
                    return

            currentClickedItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
            for parentIndex, childIndexList in self.cutIndexDict.items():
                parentItem = self._standardItemModel.itemFromIndex(parentIndex)
                parentItem = HierarchyItem(parentIndex.data(), parentItem.itemType, parentItem.uuid)

                # 检查是否是字典中最顶层的项
                for temp in list(self.cutIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    cutItemList.append([parentItem.uuid, currentClickedItem.uuid])
                    currentClickedItem.appendRow(parentItem)

                    # 找到顶层项后，开始添加子项
                    if childIndexList:
                        self._pasteItemForCutRecursively(self.cutIndexDict, childIndexList, parentItem, cutItemList)

        print(cutItemList)
        self.cutItemSignal.emit(cutItemList)

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

    def _pasteItemForCutRecursively(self, indexDict, childIndexList, parentItem, cutItemList):
        for childIndex in childIndexList:
            childItem = self._standardItemModel.itemFromIndex(childIndex)
            childItem = HierarchyItem(childIndex.data(), childItem.itemType, childItem.uuid)
            parentItem.appendRow(childItem)
            cutItemList.append([childItem.uuid, parentItem.uuid])
            if indexDict.get(childIndex):
                self._pasteItemForCutRecursively(indexDict, indexDict[childIndex], childItem, cutItemList)

    def _pasteForCopy(self):
        if not self._currentClickedIndex.isValid():
            return
            # for parentIndex, childIndexList in self.copyIndexDict.items():
            #     parentItem = HierarchyItem(parentIndex.data())
            #
            #     # 检查是否是字典中最顶层的项
            #     for temp in list(self.copyIndexDict.values()):
            #         if parentIndex in temp:
            #             break
            #     else:
            #         self._standardItemModel.appendRow(parentItem)
            #
            #     # 添加子项
            #     if childIndexList:
            #         self._pasteItemForCopyRecursively(self.copyIndexDict, childIndexList, parentItem)

        else:
            copyItemList = []   # 用于copyItemSignal
            currentClickedItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
            for parentIndex, childIndexList in self.copyIndexDict.items():
                parentItem = self._standardItemModel.itemFromIndex(parentIndex)
                parentItem = HierarchyItem(parentIndex.data(), parentItem.itemType)

                # 检查是否是字典中最顶层的项
                for temp in list(self.copyIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    copyItemList.append([parentItem.itemType, parentItem.uuid, currentClickedItem.uuid])
                    currentClickedItem.appendRow(parentItem)

                    # 找到顶层项后，开始添加子项
                    if childIndexList:
                        self._pasteItemForCopyRecursively(self.copyIndexDict, childIndexList, parentItem, copyItemList)

            self.copyItemSignal.emit(copyItemList)

    def _pasteItemForCopyRecursively(self, indexDict, childIndexList, parentItem, copyItemList):
        for childIndex in childIndexList:
            childItem = self._standardItemModel.itemFromIndex(childIndex)
            childItem = HierarchyItem(childIndex.data(), childItem.itemType)
            parentItem.appendRow(childItem)
            copyItemList.append([childItem.itemType, childItem.uuid, parentItem.uuid])
            if indexDict.get(childIndex):
                self._pasteItemForCopyRecursively(indexDict, indexDict[childIndex], childItem, copyItemList)

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

    def getAllIndexes(self):
        indexDict = {}
        for row in range(self._standardItemModel.rowCount()):
            index = self._standardItemModel.item(row, 0).index()
            self._getChildItemRecursively(indexDict, index)

        return indexDict

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self._currentClickedIndex = index

        # 右键项时也需要在场景中显示被选中的项
        self._showItemInSceneAndPropertyWindow()

        # 显示右键菜单
        if not index.isValid():
            return
            # self._contextMenu.execBlankAreaMainMenu(event.globalPos())
        else:
            self._contextMenu.execItemMainMenu(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.accept()

    def dragMoveEvent(self, event):
        ...

    def dropEvent(self, event):
        index = self.indexAt(event.pos())

        # 无法拖放到Window节点外
        # 如果需要，删除以下判断代码
        if not index.isValid():
            return

        self._currentClickedIndex = index

        # 在拖放前先判断之前是否有复制或剪切内容
        # 有的话就先保存目标拖放节点的uuid
        copyOrCut = ""
        selectedItemsUUID = []
        if self.copyIndexDict:
            copyOrCut = "copy"
            for index in self.selectedIndexes():
                uuid = self._standardItemModel.itemFromIndex(index).uuid
                selectedItemsUUID.append(uuid)
        elif self.cutIndexDict:
            copyOrCut = "cut"
            for index in self.selectedIndexes():
                uuid = self._standardItemModel.itemFromIndex(index).uuid
                selectedItemsUUID.append(uuid)

        # 拖放
        self._cut()
        self._pasteForCut()

        # 在拖放前没有复制或剪切的话
        # 就不需要更新copyIndexDict或cutIndexDict
        if not copyOrCut:
            return

        # 拖放完毕后，重新对相应节点进行复制或剪切
        # 从而更新copyIndexDict或cutIndexDict
        allIndexes = self.getAllIndexes()
        for uuid in selectedItemsUUID:
            for index in allIndexes:
                if uuid != self._standardItemModel.itemFromIndex(index).uuid:
                    continue

                self.selectionModel().select(index, QItemSelectionModel.Select)
                break

        if copyOrCut == "copy":
            self._copy()
        else:
            self._cut()

    def mousePressEvent(self, event):
        super(ItemTreeView, self).mousePressEvent(event)
        if not self.indexAt(event.pos()).isValid():
            self.clearSelection()
            self._currentClickedIndex = None
            self.selectionChangedSignal.emit([])    # 要把场景中各项的焦点清空

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

    def resizeEvent(self, event):
        super(ItemTreeView, self).resizeEvent(event)

        # resizeEvent会在窗口初始化时触发
        # 解决了信号一开始发送无效的问题
        # _isRootUUIDSent变量确保只发送一次
        if not self._isRootUUIDSent:
            self.rootItemUUIDSignal.emit(self._rootItem.uuid)
            self._isRootUUIDSent = True



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
            newItem = HierarchyItem(index.data(), item.itemType, item.uuid)

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


