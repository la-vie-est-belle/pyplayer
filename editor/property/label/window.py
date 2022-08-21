import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from editor.util import setAlignBtnEnabled
from editor.property.common.widget import PosLineEdit, TextEdit, AlignButton, FontLineEdit, ColorLineEdit


class LabelPropertyWindow(QWidget):
    updatePropertySignal = pyqtSignal(str, str, object)

    def __init__(self):
        super(LabelPropertyWindow, self).__init__()
        self._uuid = None
        self._posXLine = PosLineEdit()
        self._posYLine = PosLineEdit()
        self._textEdit = TextEdit()
        self._fontLine = FontLineEdit()
        self._colorLine = ColorLineEdit()

        self._alignLeftBtn = AlignButton(Qt.AlignLeft, "alignLeft")
        self._alignHCenterBtn = AlignButton(Qt.AlignHCenter, "alignHCenter")
        self._alignRightBtn = AlignButton(Qt.AlignRight, "alignRight")
        self._alignTopBtn = AlignButton(Qt.AlignTop, "alignTop")
        self._alignVCenterBtn = AlignButton(Qt.AlignBottom, "alignVCenter")
        self._alignBottomBtn = AlignButton(Qt.AlignVCenter, "alignBottom")
        self._hAlignBtnList = [self._alignLeftBtn, self._alignHCenterBtn, self._alignRightBtn]
        self._vAlignBtnList = [self._alignTopBtn, self._alignVCenterBtn, self._alignBottomBtn]

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(300, 600)

        self._alignLeftBtn.setEnabled(False)
        self._alignVCenterBtn.setEnabled(False)

    def _setSignal(self):
        for btn in self._hAlignBtnList:
            btn.clicked.connect(self._setHorizontalAlignment)

        for btn in self._vAlignBtnList:
            btn.clicked.connect(self._setVerticalAlignment)

        self._posXLine.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "posX", self._posXLine.text()))
        self._posYLine.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "posY", self._posYLine.text()))
        self._textEdit.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "text", self._textEdit.toPlainText()))
        self._fontLine.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "font", self._fontLine.text()))
        self._colorLine.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "color", self._colorLine.text()))

    def _setLayout(self):
        posHLayout = QHBoxLayout()
        posHLayout.addWidget(QLabel("位置: "))
        posHLayout.addWidget(QLabel("x: "))
        posHLayout.addWidget(self._posXLine)
        posHLayout.addStretch()
        posHLayout.addWidget(QLabel("y: "))
        posHLayout.addWidget(self._posYLine)

        textVLayout = QVBoxLayout()
        textVLayout.addWidget(QLabel("文本: "))
        textVLayout.addWidget(self._textEdit)

        fontHLayout = QHBoxLayout()
        fontHLayout.addWidget(QLabel("字体: "))
        fontHLayout.addWidget(self._fontLine)

        colorHLayout = QHBoxLayout()
        colorHLayout.addWidget(QLabel("颜色: "))
        colorHLayout.addWidget(self._colorLine)

        alignBtnHLayout1 = QHBoxLayout()
        alignBtnHLayout2 = QHBoxLayout()
        alignBtnHLayout1.addWidget(QLabel("水平对齐: "))
        alignBtnHLayout1.addWidget(self._alignLeftBtn)
        alignBtnHLayout1.addWidget(self._alignHCenterBtn)
        alignBtnHLayout1.addWidget(self._alignRightBtn)
        alignBtnHLayout2.addWidget(QLabel("垂直对齐: "))
        alignBtnHLayout2.addWidget(self._alignTopBtn)
        alignBtnHLayout2.addWidget(self._alignVCenterBtn)
        alignBtnHLayout2.addWidget(self._alignBottomBtn)

        windowVLayout = QVBoxLayout(self)
        windowVLayout.addLayout(posHLayout)
        windowVLayout.addLayout(textVLayout)
        windowVLayout.addLayout(fontHLayout)
        windowVLayout.addLayout(colorHLayout)
        windowVLayout.addLayout(alignBtnHLayout1)
        windowVLayout.addLayout(alignBtnHLayout2)

    def setProperties(self, properties):
        """设置属性窗口上的各个控件值"""
        self._uuid = properties["uuid"]
        self._posXLine.setText(str(properties["posX"]))
        self._posYLine.setText(str(properties["posY"]))
        self._textEdit.setText(properties["text"])
        self._fontLine.setText(properties["font"])
        self._colorLine.setColor(QColor(properties["color"]))
        setAlignBtnEnabled(self._hAlignBtnList, self._vAlignBtnList, properties["alignment"])

    def _setHorizontalAlignment(self):
        horizontalAlignment = None
        for btn in self._hAlignBtnList:
            if btn == self.sender():
                btn.setEnabled(False)
                horizontalAlignment = btn.alignType
            else:
                btn.setEnabled(True)

        verticalAlignment = None
        for btn in self._vAlignBtnList:
            if not btn.isEnabled():
                verticalAlignment = btn.alignType
                break

        self.updatePropertySignal.emit(self._uuid, "alignment", horizontalAlignment | verticalAlignment)

    def _setVerticalAlignment(self):
        verticalAlignment = None
        for btn in self._vAlignBtnList:
            if btn == self.sender():
                btn.setEnabled(False)
                verticalAlignment = btn.alignType
            else:
                btn.setEnabled(True)

        horizontalAlignment = None
        for btn in self._hAlignBtnList:
            if not btn.isEnabled():
                horizontalAlignment = btn.alignType
                break

        self.updatePropertySignal.emit(self._uuid, "alignment", horizontalAlignment | verticalAlignment)

    def _updatePosX(self):
        x = int(self._posXLine.text())
        self.updateLabelPosXSignal.emit(x)

    def _updatePosY(self):
        y = int(self._posXLine.text())
        self.updateLabelPosXSignal.emit(y)


if __name__ == "__main__":
    app = QApplication([])
    window = LabelPropertyWindow()
    window.show()

    qss_path = str(Path().absolute().parent.parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())
