import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.item.label import Label
from editor.scene.custom.widget import WindowSizeControl


class SceneWindow(QGraphicsView):

    def __init__(self):
        super(SceneWindow, self).__init__()
        self._uuid = None
        self._allItemsList = [self]
        self._scene = QGraphicsScene()
        self._windowSizeControl = WindowSizeControl(self)

        self._startX = None
        self._startY = None

        self._setUI()

    @property
    def uuid(self):
        return self._uuid

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.setScene(self._scene)
        self.setFixedSize(600, 400)
        self._scene.setSceneRect(0, 0, self.width(), self.height())
        self.setObjectName("sceneWindow")

        brush = QBrush(QColor(236, 236, 236))
        self._scene.setBackgroundBrush(brush)

    def _setSignal(self):
        self._windowSizeControl.sizeChangedSignal.connect(self._resize)

    def _setLayout(self):
        x = self.width()-self._windowSizeControl.width()
        y = self.height()-self._windowSizeControl.height()
        self._windowSizeControl.move(x, y)

    def _resize(self, widthChangedValue, heightChangedValue):
        newWidth = self.width() + widthChangedValue
        newHeight = self.height() + heightChangedValue

        if newWidth <= 100 or newHeight <= 50:
            return

        self.setFixedSize(newWidth, newHeight)
        self._scene.setSceneRect(0, 0, newWidth, newHeight)

    # 发不出去，暂时先不管Window的uuid
    # def setRootWindowUUID(self, uuid):
    #     print(444)
    #     self._uuid = uuid
    #     print(self._uuid)

    def createNewItem(self, name, uuid, parentUUID):
        if name == "Label":
            self._createLabel(uuid, parentUUID)

    def _createLabel(self, uuid, parentUUID):
        item = self._getItemByUUID(parentUUID)
        if item:
            label = Label(uuid, item)
            label.setPos(10, 10)
        else:
            label = Label(uuid)
            label.setPos(10, 10)
            self._scene.addItem(label)

    def _getItemByUUID(self, uuid):
        for item in self.items():
            if item.uuid == uuid:
                return item
        return None

    # def mousePressEvent(self, event):
    #     super(SceneWindow, self).mousePressEvent(event)
    #     self._startX = event.x()
    #     self._startY = event.y()
    #     event.accept()
    #
    # def mouseMoveEvent(self, event):
    #     super(SceneWindow, self).mouseMoveEvent(event)
    #     disX = event.x() - self._startX
    #     disY = event.y() - self._startY
    #     self.move(self.x()+disX, self.y()+disY)
    #     event.accept()

    def resizeEvent(self, event):
        """始终确保尺寸调节控件位于窗口右下角"""
        super(SceneWindow, self).resizeEvent(event)
        self._setLayout()


if __name__ == "__main__":
    app = QApplication([])
    window = SceneWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:
        window.setStyleSheet(f.read())

    sys.exit(app.exec())
