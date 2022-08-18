from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Label(QGraphicsProxyWidget):
    def __init__(self, uuid, parentItem=None):
        super(Label, self).__init__(parentItem)
        self._uuid = uuid
        self._startX = None
        self._startY = None
        self._label = QLabel("Label")

        self._setUI()

    @property
    def uuid(self):
        return self._uuid

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setWidget(self._label)
        self.setObjectName("itemLabel")
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self._label.setAttribute(Qt.WA_TranslucentBackground)

    def _setSignal(self):
        ...

    def mousePressEvent(self, event):
        super(Label, self).mousePressEvent(event)
        self._startX = event.pos().x()
        self._startY = event.pos().y()
        event.accept()

    def mouseMoveEvent(self, event):
        super(Label, self).mouseMoveEvent(event)
        disX = event.pos().x() - self._startX
        disY = event.pos().y() - self._startY
        self.moveBy(disX, disY)

    def hoverEnterEvent(self, event):
        super(Label, self).hoverEnterEvent(event)
        self.widget().setCursor(Qt.OpenHandCursor)

    def grabMouseEvent(self, event):
        super(Label, self).grabMouseEvent(event)
        self.setCursor(Qt.ClosedHandCursor)

    def ungrabMouseEvent(self, event):
        super(Label, self).ungrabMouseEvent(event)
        self.setCursor(Qt.OpenHandCursor)