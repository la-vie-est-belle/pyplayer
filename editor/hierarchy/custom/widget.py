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
        # ??????????????????????????????
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
        choice = QMessageBox.question(self, '??????', '?????????????????????', QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.No:
            return

        itemsToDelete = []
        deletedUUIDList = []
        for index in self.selectedIndexes():
            item = self._standardItemModel.itemFromIndex(index)
            itemsToDelete.append(item)
            deletedUUIDList.append(item.uuid)

            # ???????????????????????????Window?????????
            # if index.data() == "Window":
            #     QMessageBox.critical(self, '??????', '????????????????????????', QMessageBox.Ok)
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
                # ?????????????????????????????????????????????RuntimeError
                # ????????????try-except?????????
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
            #     # ???????????????????????????????????????
            #     for temp in list(self.cutIndexDict.values()):
            #         if parentIndex in temp:
            #             break
            #     else:
            #         self._standardItemModel.appendRow(parentItem)
            #
            #     # ????????????
            #     if childIndexList:
            #         self._pasteItemForCutRecursively(self.cutIndexDict, childIndexList, parentItem)

        else:
            # ????????????????????????????????????
            # ??????????????????????????????????????????????????????
            cutItemList = []
            for parentIndex, childIndexList in self.cutIndexDict.items():
                if self._currentClickedIndex in childIndexList:
                    QMessageBox.critical(self, "??????", "?????????????????????????????????", QMessageBox.Yes)
                    self.cutIndexDict.clear()
                    return
                elif self._currentClickedIndex == parentIndex:
                    self.cutIndexDict.clear()
                    return

            currentClickedItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
            for parentIndex, childIndexList in self.cutIndexDict.items():
                parentItem = self._standardItemModel.itemFromIndex(parentIndex)
                parentItem = HierarchyItem(parentIndex.data(), parentItem.itemType, parentItem.uuid)

                # ???????????????????????????????????????
                for temp in list(self.cutIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    cutItemList.append([parentItem.uuid, currentClickedItem.uuid])
                    currentClickedItem.appendRow(parentItem)

                    # ???????????????????????????????????????
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
            #     # ???????????????????????????????????????
            #     for temp in list(self.copyIndexDict.values()):
            #         if parentIndex in temp:
            #             break
            #     else:
            #         self._standardItemModel.appendRow(parentItem)
            #
            #     # ????????????
            #     if childIndexList:
            #         self._pasteItemForCopyRecursively(self.copyIndexDict, childIndexList, parentItem)

        else:
            copyItemList = []   # ??????copyItemSignal
            currentClickedItem = self._standardItemModel.itemFromIndex(self._currentClickedIndex)
            for parentIndex, childIndexList in self.copyIndexDict.items():
                parentItem = self._standardItemModel.itemFromIndex(parentIndex)
                parentItem = HierarchyItem(parentIndex.data(), parentItem.itemType)

                # ???????????????????????????????????????
                for temp in list(self.copyIndexDict.values()):
                    if parentIndex in temp:
                        break
                else:
                    copyItemList.append([parentItem.itemType, parentItem.uuid, currentClickedItem.uuid])
                    currentClickedItem.appendRow(parentItem)

                    # ???????????????????????????????????????
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

        # ??????????????????????????????????????????????????????
        self._showItemInSceneAndPropertyWindow()

        # ??????????????????
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

        # ???????????????Window?????????
        # ???????????????????????????????????????
        if not index.isValid():
            return

        self._currentClickedIndex = index

        # ?????????????????????????????????????????????????????????
        # ??????????????????????????????????????????uuid
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

        # ??????
        self._cut()
        self._pasteForCut()

        # ???????????????????????????????????????
        # ??????????????????copyIndexDict???cutIndexDict
        if not copyOrCut:
            return

        # ????????????????????????????????????????????????????????????
        # ????????????copyIndexDict???cutIndexDict
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
            self.selectionChangedSignal.emit([])    # ????????????????????????????????????

    def drawRow(self, painter, option, index):
        """????????????????????????????????????"""
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

        # resizeEvent??????????????????????????????
        # ?????????????????????????????????????????????
        # _isRootUUIDSent???????????????????????????
        if not self._isRootUUIDSent:
            self.rootItemUUIDSignal.emit(self._rootItem.uuid)
            self._isRootUUIDSent = True



class SearchComboBox(QComboBox):
    def __init__(self):
        super(SearchComboBox, self).__init__()
        self._searchChoice = "??????"
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.addItems(["??????", "UUID"])

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
        self.setPlaceholderText("?????????")
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

            # ?????????????????????????????????tooltip???????????????????????????
            # ???????????????UUID????????????tooltip???????????????UUID
            toolTip = index.data()
            if searchComboBoxText == "??????":
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


