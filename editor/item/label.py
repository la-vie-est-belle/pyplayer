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
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setWidget(self._label)
        self.setObjectName("itemLabel")
        self._label.setAttribute(Qt.WA_TranslucentBackground)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 105, 217, 20))
        self.setPalette(palette)

    def _setSignal(self):
        ...

    def getProperties(self):
        properties = {
            "type": "Label",
            "uuid": self._uuid,
            "posX": int(self.x()),
            "posY": int(self.y()),
            "text": self._label.text(),
            "font": f'{self._label.font().family()} ; {self._label.font().pointSize()}',
            "color": self._label.palette().color(QPalette.WindowText).name(),
            "alignment": int(self._label.alignment()),
        }

        return properties

    def updateProperty(self, property, value):
        if property == "posX":
            if not value:
                self.setX(0)
            elif value == "-":
                ...
            else:
                self.setX(int(value))

        elif property == "posY":
            if not value:
                self.setY(0)
            elif value == "-":
                ...
            else:
                self.setY(int(value))

        elif property == "text":
            self._label.setText(value)
            self._label.adjustSize()

        elif property == "font":
            font = QFont()
            font.setFamily(value.split(";")[0].strip())
            font.setPointSize(int(value.split(";")[1].strip()))
            self._label.setFont(font)
            self._label.adjustSize()

        elif property == "color":
            palette = self._label.palette()
            palette.setColor(QPalette.WindowText, QColor(value))
            self._label.setPalette(palette)

        elif property == "alignment":
            self._label.setAlignment(value)

    def setSelected(self, selected):
        super(Label, self).setSelected(selected)

        if selected:
            # 有焦点的话可以让item在框选时显示属性
            # 不过在ctrl键按下时有bug，属性窗口更新不及时
            # self.setFocus(Qt.OtherFocusReason)
            self.setAutoFillBackground(True)
        else:
            # self.clearFocus()
            self.setAutoFillBackground(False)

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

    def hoverLeaveEvent(self, event):
        super(Label, self).hoverLeaveEvent(event)

    def grabMouseEvent(self, event):
        super(Label, self).grabMouseEvent(event)
        self.setCursor(Qt.ClosedHandCursor)

    def ungrabMouseEvent(self, event):
        super(Label, self).ungrabMouseEvent(event)
        self.setCursor(Qt.OpenHandCursor)