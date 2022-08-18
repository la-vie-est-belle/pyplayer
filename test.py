import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Label(QLabel):
    def __init__(self, str, parent):
        super(Label, self).__init__(str, parent)
        self._startX = None
        self._startY = None

    def mousePressEvent(self, event):
        super(Label, self).mousePressEvent(event)
        self._startX = event.x()
        self._startY = event.y()
        event.accept()

    def mouseMoveEvent(self, event):
        super(Label, self).mouseMoveEvent(event)
        disX = event.x() - self._startX
        disY = event.y() - self._startY
        self.move(self.x()+disX, self.y()+disY)
        event.accept()


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.resize(500, 500)
        self.label = Label("Label Parent", self)
        self.label.move(100, 100)
        # self.label.setAttribute(Qt.WA_PaintOnScreen)


        self.label2 = Label("Child", self.label)
        # self.label2.move(50, 50)
        self.label2.setAttribute(Qt.WA_OutsideWSRange)




if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())