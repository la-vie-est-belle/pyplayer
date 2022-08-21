from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.property.root.window import RootPropertyWindow
from editor.property.label.window import LabelPropertyWindow


class PropertyWindow(QWidget):
    updatePropertySignal = pyqtSignal(str, str, object)

    def __init__(self):
        super(PropertyWindow, self).__init__()
        self._rootPropertyWindow = RootPropertyWindow()
        self._labelPropertyWindow = LabelPropertyWindow()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self._labelPropertyWindow.hide()

    def _setSignal(self):
        self._rootPropertyWindow.updatePropertySignal.connect(self.updatePropertySignal.emit)
        self._labelPropertyWindow.updatePropertySignal.connect(self.updatePropertySignal.emit)

    def _setLayout(self):
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(self._rootPropertyWindow)
        vLayout.addWidget(self._labelPropertyWindow)
        vLayout.setContentsMargins(0, 0, 0, 0)

    def showPropertyWindow(self, properties):
        if not properties:
            self._rootPropertyWindow.show()
            self._labelPropertyWindow.hide()
            return

        if properties["type"] == "Root":
            self._rootPropertyWindow.show()
            self._labelPropertyWindow.hide()
            self._rootPropertyWindow.setProperties(properties)

        elif properties["type"] == "Label":
            self._rootPropertyWindow.hide()
            self._labelPropertyWindow.show()
            self._labelPropertyWindow.setProperties(properties)