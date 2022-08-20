from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Scene(QGraphicsScene):
    showPropertySignal = pyqtSignal(dict)
    selectionChangedSignal = pyqtSignal(list)

    def __init__(self):
        super(Scene, self).__init__()
        self._isCtrlPressed = False
        self._selectedItemsList = []

    def mousePressEvent(self, event):
        super(Scene, self).mousePressEvent(event)

        focusItem = self.focusItem()
        selectedUUIDList = []
        if not focusItem:
            # self.showPropertySignal.emit({})
            self.selectionChangedSignal.emit(selectedUUIDList)
            for item in self.items():
                item.setSelected(False)
            return

        if self._isCtrlPressed:
            if focusItem in self.selectedItems():
                focusItem.setSelected(False)
            else:
                focusItem.setSelected(True)
        else:
            for item in self.items():
                item.setSelected(False)
            focusItem.setSelected(True)

        for item in self.selectedItems():
            selectedUUIDList.append(item.uuid)

        self.showPropertySignal.emit(focusItem.getProperties())
        self.selectionChangedSignal.emit(selectedUUIDList)

    def keyPressEvent(self, event):
        super(Scene, self).keyPressEvent(event)
        if event.key() == Qt.Key.Key_Control:
            self._isCtrlPressed = True

    def keyReleaseEvent(self, event):
        super(Scene, self).keyReleaseEvent(event)
        if event.key() == Qt.Key.Key_Control:
            self._isCtrlPressed = False





class WindowSizeControl(QWidget):
    sizeChangedSignal = pyqtSignal(int, int)

    def __init__(self, parent):
        super(WindowSizeControl, self).__init__(parent)
        self._startX = None
        self._startY = None
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.setFixedSize(15, 15)
        self.setToolTip("拉动改变窗口大小")
        self.setCursor(Qt.SizeFDiagCursor)
        self.setObjectName("sceneWindowSizeControl")
        self.setAttribute(Qt.WA_TranslucentBackground)

    def _setSignal(self):
        ...

    def _setLayout(self):
        ...

    def paintEvent(self, event):
        super(WindowSizeControl, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0, 255))
        painter.drawLine(QPointF(0, self.height()), QPointF(self.width(), 0))
        painter.drawLine(QPointF(self.width()/4, self.height()), QPointF(self.width(), self.height()/4))
        painter.drawLine(QPointF(self.width()/2, self.height()), QPointF(self.width(), self.height()/2))
        painter.drawLine(QPointF(self.width()-3, self.height()), QPointF(self.width(), self.height()-3))

    def mousePressEvent(self, event):
        super(WindowSizeControl, self).mousePressEvent(event)
        self._startX = event.x()
        self._startY = event.y()

    def mouseMoveEvent(self, event):
        super(WindowSizeControl, self).mouseMoveEvent(event)
        widthChangedValue = event.x() - self._startX
        heightChangedValue = event.y() - self._startY
        self.sizeChangedSignal.emit(widthChangedValue, heightChangedValue)
        event.accept()
