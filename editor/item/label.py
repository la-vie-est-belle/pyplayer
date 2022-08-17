from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Label(QLabel):
    def __init__(self, str, uuid, parent):
        super(Label, self).__init__(str, parent)
        self._uuid = uuid
        self._startX = None
        self._startY = None

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.setObjectName("itemLabel")
        self.setFocus(Qt.MouseFocusReason)

    def _setSignal(self):
        ...

    def mousePressEvent(self, event):
        super(Label, self).mousePressEvent(event)
        self._startX = event.x()
        self._startY = event.y()

    def mouseMoveEvent(self, event):
        super(Label, self).mouseMoveEvent(event)
        disX = event.x() - self._startX
        disY = event.y() - self._startY
        self.move(self.x()+disX, self.y()+disY)