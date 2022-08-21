import sys
from pathlib import Path

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from editor.scene.window import SceneWindow
from editor.asset.window import AssetWindow
from editor.console.window import ConsoleWindow
from editor.hierarchy.window import HierarchyWindow
from editor.property.window import PropertyWindow
from editor.custom.widget import SceneWindowBase
from editor.custom.widget import Gizmo


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
        self._propertyWindow = PropertyWindow()
        self._gizmo = Gizmo(self._sceneWindow)

        self._mainWindowCentralWidget = QWidget()

        self.setUI()

    def setUI(self):
        self._setWidget()
        self._setSignal()
        self._setLayout()

    def _setWidget(self):
        self.resize(1430, 800)
        self.setWindowTitle("PyPlayer")
        self.setCentralWidget(self._mainWindowCentralWidget)

        self._leftTopWindowTab.setObjectName("editorTab")
        self._leftBottomWindowTab.setObjectName("editorTab")
        self._centerTopWindowTab.setObjectName("editorTab")
        self._centerBottomWindowTab.setObjectName("editorTab")
        self._rightWindowTab.setObjectName("editorTab")

        self._leftTopWindowTab.addTab(self._hierarchyWindow, "层级窗口")
        self._leftBottomWindowTab.addTab(self._assetWindow, "资源窗口")
        self._centerTopWindowTab.addTab(self._sceneWindowBase, "场景窗口")
        self._centerBottomWindowTab.addTab(self._consoleWindow, "日志窗口")
        self._rightWindowTab.addTab(self._propertyWindow, "属性窗口")

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
        self._leftCenterRightWindowsSplitter.setSizes([260, 820, 350])

    def _setSignal(self):
        self._hierarchyWindow.rootItemSignal.connect(self._sceneWindow.setRootWindowUUID)
        self._hierarchyWindow.cutItemSignal.connect(self._sceneWindow.resetItemParent)
        self._hierarchyWindow.copyItemSignal.connect(self._sceneWindow.copyItems)
        self._hierarchyWindow.newItemSignal.connect(self._sceneWindow.createNewItem)
        self._hierarchyWindow.deleteItemSignal.connect(self._sceneWindow.deleteItems)
        self._hierarchyWindow.selectionChangedSignal.connect(self._sceneWindow.selectItems)

        self._sceneWindow.showPropertySignal.connect(self._propertyWindow.showPropertyWindow)
        self._sceneWindow.selectionChangedSignal.connect(self._hierarchyWindow.selectItems)

        self._propertyWindow.updatePropertySignal.connect(self._sceneWindow.updateProperty)


    def _setLayout(self):
        windowHLayout = QHBoxLayout(self._mainWindowCentralWidget)
        windowHLayout.addWidget(self._leftCenterRightWindowsSplitter)

        self._sceneWindow.setParent(self._sceneWindowBase)
        self._sceneWindow.move(100, 40)

        # gizmo设置在sceneWindow左上角
        self._gizmo.setParent(self._sceneWindowBase)
        x = int(self._sceneWindow.x()-self._gizmo.width()/2)
        y = int(self._sceneWindow.y()-self._gizmo.height()/2)
        self._gizmo.move(x, y)


if __name__ == "__main__":
    app = QApplication([])
    window = EditorWindow()
    window.show()

    qss_path = str(Path().absolute().parent / "editor/res/editor.qss")
    with open (qss_path, "r", encoding="utf-8") as f:

        window.setStyleSheet(f.read())
    sys.exit(app.exec())
