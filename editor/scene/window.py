import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.item.label import Label
from editor.scene.custom.widget import Scene, WindowSizeControl


class SceneWindow(QGraphicsView):
    showPropertySignal = pyqtSignal(dict)
    selectionChangedSignal = pyqtSignal(list)

    def __init__(self):
        super(SceneWindow, self).__init__()
        self._uuid = None
        self._scene = Scene()
        self._allItemsList = [self]
        self._windowSizeControl = WindowSizeControl(self)

        self._setUI()

    @property
    def uuid(self):
        return self._uuid

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.setObjectName("sceneWindow")
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setScene(self._scene)
        self.setFixedSize(600, 400)
        self._scene.setSceneRect(0, 0, self.width(), self.height())

        brush = QBrush(QColor(236, 236, 236))
        self._scene.setBackgroundBrush(brush)

    def _setSignal(self):
        self._windowSizeControl.sizeChangedSignal.connect(self._resize)
        self._scene.showPropertySignal.connect(self.showPropertySignal.emit)
        self._scene.selectionChangedSignal.connect(self.selectionChangedSignal.emit)

    def _setLayout(self):
        x = self.width()-self._windowSizeControl.width()
        y = self.height()-self._windowSizeControl.height()
        self._windowSizeControl.move(x, y)

    def _resize(self, widthChangedValue, heightChangedValue):
        newWidth = self.width() + widthChangedValue
        newHeight = self.height() + heightChangedValue

        if newWidth < 0 or newHeight < 0:
            return

        self.setFixedSize(newWidth, newHeight)
        self._scene.setSceneRect(0, 0, newWidth, newHeight)

    def getProperties(self):
        properties = {
            "type": "Root",
            "uuid": self._uuid,
            "posX": int(self.x()),
            "posY": int(self.y()),
            "width": int(self.width()),
            "height": int(self.height())
        }

        return properties

    def setRootWindowUUID(self, uuid):
        self._uuid = uuid

    def deleteItems(self, deletedUUIDList):
        for uuid in deletedUUIDList:
            item = self._getItemByUUID(uuid)
            self._scene.removeItem(item)

    def resetItemParent(self, cutItemList):
        # ??????uuid????????????????????????
        for itemInfo in cutItemList:
            childItem = self._getItemByUUID(itemInfo[0])
            newParentItem = self._getItemByUUID(itemInfo[1])
            if newParentItem:
                childItem.setParentItem(newParentItem)
            else:
                self._scene.removeItem(childItem)
                self._scene.addItem(childItem)

                # ??????????????????0????????????????????????
                # ?????????????????????PyQt?????????????????????0
                # childItem.setParentItem(0)

            childItem.setPos(10, 10)

    def copyItems(self, copyItemList):
        for itemInfo in copyItemList:
            self.createNewItem(itemInfo[0], itemInfo[1], itemInfo[2])

    def createNewItem(self, itemType, uuid, parentUUID):
        if itemType == "Label":
            newItem = self._createLabel(uuid, parentUUID)

        # ????????????????????????????????????????????????
        self.showPropertySignal.emit(newItem.getProperties())

    def _createLabel(self, uuid, parentUUID):
        item = self._getItemByUUID(parentUUID)
        if item:
            label = Label(uuid, item)
            label.setPos(10, 10)
        else:
            label = Label(uuid)
            label.setPos(10, 10)
            self._scene.addItem(label)

        return label

    def _getItemByUUID(self, uuid):
        for item in self.items():
            if item.uuid == uuid:
                return item
        return None

    def selectItems(self, selectedUUIDList):
        for item in self._scene.items():
            item.setSelected(False)

        # ??????????????????????????????????????????
        if not selectedUUIDList:
            self.showPropertySignal.emit(self.getProperties())
            return

        for item in self._scene.items():
            if item.uuid in selectedUUIDList:
                item.setSelected(True)

        # ???selectedUUIDList???????????????item??????focusItem
        # ????????????item???????????????
        focusItem = self._getItemByUUID(selectedUUIDList[-1])
        self.showPropertySignal.emit(focusItem.getProperties())

    def updateProperty(self, uuid, property, value):
        # ??????????????????
        # ?????????????????????uuid?????????None
        if not uuid or uuid == self._uuid:
            self._updateRootWindowProperty(property, value)
            return

        # ???????????????
        item = self._getItemByUUID(uuid)
        item.updateProperty(property, value)

    def _updateRootWindowProperty(self, property, value):
        if property == "width":
            if not value:
                self.setFixedWidth(0)
            else:
                self.setFixedWidth(int(value))
            self._scene.setSceneRect(0, 0, self.width(), self.height())

        elif property == "height":
            if not value:
                self.setFixedHeight(0)
            else:
                self.setFixedHeight(int(value))
            self._scene.setSceneRect(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        """???????????????????????????????????????????????????"""
        super(SceneWindow, self).resizeEvent(event)
        self._setLayout()

        # resizeEvent??????????????????????????????
        # ?????????????????????????????????????????????????????????
        # ?????????????????????????????????????????????
        self.showPropertySignal.emit(self.getProperties())


if __name__ == "__main__":
    app = QApplication([])
    window = SceneWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:
        window.setStyleSheet(f.read())

    sys.exit(app.exec())
