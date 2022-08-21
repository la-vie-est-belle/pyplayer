import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.property.common.widget import ObjectNameLine, SizeLineEdit


class RootPropertyWindow(QWidget):
    updatePropertySignal = pyqtSignal(str, str, object)

    def __init__(self):
        super(RootPropertyWindow, self).__init__()
        self._uuid = None
        self._objectNameLine = ObjectNameLine("Window")
        self._widthLine = SizeLineEdit()
        self._heightLine = SizeLineEdit()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(300, 600)
        self._objectNameLine.setReadOnly(True)  # 根节点对象名称无法修改

    def _setSignal(self):
        self._widthLine.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "width", self._widthLine.text()))
        self._heightLine.textChanged.connect(lambda: self.updatePropertySignal.emit(self._uuid, "height", self._heightLine.text()))
        ...

    def _setLayout(self):
        objectNameHLayout = QHBoxLayout()
        objectNameHLayout.addWidget(QLabel("对象名: "))
        objectNameHLayout.addWidget(self._objectNameLine)

        sizeHLayout = QHBoxLayout()
        sizeHLayout.addWidget(QLabel("大小: "))
        sizeHLayout.addWidget(QLabel("宽: "))
        sizeHLayout.addWidget(self._widthLine)
        sizeHLayout.addWidget(QLabel("高: "))
        sizeHLayout.addWidget(self._heightLine)

        windowVLayout = QVBoxLayout(self)
        windowVLayout.addLayout(objectNameHLayout)
        windowVLayout.addLayout(sizeHLayout)
        windowVLayout.addStretch()

    def setProperties(self, properties):
        """设置属性窗口上的各个控件值"""
        self._uuid = properties["uuid"]
        self._widthLine.setText(str(properties["width"]))
        self._heightLine.setText(str(properties["height"]))


if __name__ == "__main__":
    app = QApplication([])
    window = RootPropertyWindow()
    window.show()

    qss_path = str(Path().absolute().parent.parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())
