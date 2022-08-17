import sys
from pathlib import Path

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from editor.scene.window import SceneWindow
from editor.asset.window import AssetWindow
from editor.console.window import ConsoleWindow
from editor.hierarchy.window import HierarchyWindow
from editor.custom.widget import SceneWindowBase


class EditorWindow(QMainWindow):
    def __init__(self):
        super(EditorWindow, self).__init__()
        self._leftWindowsSplitter = QSplitter()
        self._centerWindowsSplitter = QSplitter()
        self._leftCenterRightWindowsSplitter = QSplitter()

        self._leftTopWindowTab = QTabWidget()
        self._leftBottomWindowTab = QTabWidget()
        self._centerTopWindowTab = QTabWidget()
        self._centerBottomWindowTab = QTabWidget()
        self._rightWindowTab = QTabWidget()

        self._assetWindow = AssetWindow()
        self._sceneWindow = SceneWindow()
        self._consoleWindow = ConsoleWindow()
        self._hierarchyWindow = HierarchyWindow()
        self._sceneWindowBase = SceneWindowBase()

        self._widget = QWidget()

        self.setUI()

    def setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(1430, 800)
        self.setWindowTitle("PyPlayer")
        self.setCentralWidget(self._widget)

    def _setSignal(self):
        self._leftTopWindowTab.setObjectName("editorTab")
        self._leftBottomWindowTab.setObjectName("editorTab")
        self._centerTopWindowTab.setObjectName("editorTab")
        self._centerBottomWindowTab.setObjectName("editorTab")
        self._rightWindowTab.setObjectName("editorTab")

        self._leftTopWindowTab.addTab(self._hierarchyWindow, "层级窗口")
        self._leftBottomWindowTab.addTab(self._assetWindow, "资源窗口")
        self._centerTopWindowTab.addTab(self._sceneWindowBase, "场景窗口")
        self._centerBottomWindowTab.addTab(self._consoleWindow, "日志窗口")
        self._rightWindowTab.addTab(QWidget(), "属性窗口")

        self._leftWindowsSplitter.addWidget(self._leftTopWindowTab)
        self._leftWindowsSplitter.addWidget(self._leftBottomWindowTab)
        self._leftWindowsSplitter.setOrientation(Qt.Vertical)

        self._centerWindowsSplitter.addWidget(self._centerTopWindowTab)
        self._centerWindowsSplitter.addWidget(self._centerBottomWindowTab)
        self._centerWindowsSplitter.setOrientation(Qt.Vertical)
        self._centerWindowsSplitter.setSizes([550, 250])

        self._leftCenterRightWindowsSplitter.addWidget(self._leftWindowsSplitter)
        self._leftCenterRightWindowsSplitter.addWidget(self._centerWindowsSplitter)
        self._leftCenterRightWindowsSplitter.addWidget(self._rightWindowTab)
        self._leftCenterRightWindowsSplitter.setSizes([280, 800, 350])

    def _setLayout(self):
        windowHLayout = QHBoxLayout(self._widget)
        windowHLayout.addWidget(self._leftCenterRightWindowsSplitter)

        sceneWindowHLayout = QHBoxLayout(self._sceneWindowBase)
        sceneWindowHLayout.addWidget(self._sceneWindow)

if __name__ == "__main__":
    app = QApplication([])
    window = EditorWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "editor/res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())
