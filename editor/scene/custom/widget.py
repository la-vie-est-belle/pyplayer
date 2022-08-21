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

    def mousePressEvent(self, event):
        """针对ctrl键多选"""
        super(Scene, self).mousePressEvent(event)

        focusItem = self.focusItem()
        selectedUUIDList = []
        if not focusItem:
            self.showPropertySignal.emit({})
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

    def mouseMoveEvent(self, event):
        super(Scene, self).mouseMoveEvent(event)

        # 当鼠标从层级窗口移动到场景窗口时
        # mouseMoveEvent不知道会什么会被触发
        # 这会导致某个item的属性窗口被显示出来
        # 所以先暂时不在该事件中更新属性窗口

        # 移动过程中更新属性窗口
        # focusItem = self.focusItem()
        # if focusItem:
        #     self.showPropertySignal.emit(focusItem.getProperties())

    def mouseReleaseEvent(self, event):
        """针对框选"""
        super(Scene, self).mouseReleaseEvent(event)

        # 框选
        selectedUUIDLIst = []
        for item in self.selectedItems():
            selectedUUIDLIst.append(item.uuid)
            item.setSelected(True)
        self.selectionChangedSignal.emit(selectedUUIDLIst)

        # 移动结束后更新属性窗口
        focusItem = self.focusItem()
        if focusItem:
            self.showPropertySignal.emit(focusItem.getProperties())

    def mouseDoubleClickEvent(self, event):
        """
        在场景中双击某个项时，
        层级窗口中的项会在选中和不选中之间切换。
        为了避免这种现象，这里让mouseDoubleClickEvent无效
        """
        pass

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
