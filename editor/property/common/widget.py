from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class PosLineEdit(QLineEdit):
    def __init__(self):
        super(PosLineEdit, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.setText("0")
        self.setValidator(QRegExpValidator(QRegExp('-?[0-9]+')))

    def contextMenuEvent(self, evnet):
        pass
    
    
class TextEdit(QTextEdit):
    def __init__(self):
        super(TextEdit, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.setPlaceholderText("请输入文本...")


class AlignButton(QPushButton):
    def __init__(self, alignType):
        super(AlignButton, self).__init__()
        self._alignType = alignType
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self._setIcon()

    def _setIcon(self):
        iconPath = Path(__file__).parent.parent.parent / f"res/property/{self._alignType}.png"
        self.setIcon(QIcon(str(iconPath)))


class FontLineEdit(QLineEdit):
    def __init__(self):
        super(FontLineEdit, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.setText(f'{self.font().family()} ; {self.font().pointSize()}')
        self.setReadOnly(True)

    def mousePressEvent(self, event):
        super(FontLineEdit, self).mousePressEvent(event)
        fontDialog = QFontDialog()
        fontDialog.move(self.pos())
        font, ok = fontDialog.getFont()
        if ok:
            self.setText(f'{font.family()} ; {font.pointSize()}')

    def contextMenuEvent(self, event):
        pass


class ColorLineEdit(QLineEdit):
    def __init__(self):
        super(ColorLineEdit, self).__init__()
        self._setUI()

    def _setUI(self):
        self._setWidget()

    def _setWidget(self):
        self.setReadOnly(True)
        self.setColor(QColor(0, 0, 0))

    def setColor(self, color):
        palette = self.palette()
        palette.setBrush(QPalette.Base, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setToolTip(color.name())
        self.setText(color.name())

    def mousePressEvent(self, event):
        super(ColorLineEdit, self).mousePressEvent(event)
        colorDialog = QColorDialog()
        colorDialog.move(self.pos())
        color = QColorDialog.getColor()
        if color.isValid():
            self.setColor(color)

    def contextMenuEvent(self, event):
        pass
