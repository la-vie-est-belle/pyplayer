import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.item.label import Label


class SceneWindow(QWidget):
    def __init__(self):
        super(SceneWindow, self).__init__()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        ...

    def _setSignal(self):
        ...

    def _addItem(self, name):
        if name == "Label":
            label = Label("Label", None, self)
            label.move(20, 20)
            label.show()


    def _addLabel(self):
        ...

    def mousePressEvent(self, event):
        super(SceneWindow, self).mousePressEvent(event)



if __name__ == "__main__":
    app = QApplication([])
    window = SceneWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:
        window.setStyleSheet(f.read())

    sys.exit(app.exec())
