import shutil
import sys
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .menu import ProjectTreeViewMenu


class ProjectTreeView(QTreeView):
    def __init__(self):
        super(ProjectTreeView, self).__init__()
        self._projectPath = "/Users/louis/Desktop/pyplayer"
        self._fileSystemModel = QFileSystemModel()
        self._clipboard = QApplication.clipboard()
        self._contextMenu = ProjectTreeViewMenu()
        self._currentClickedIndex = None

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setPath(self._projectPath)

    def _setWidget(self):
        self.setObjectName("projectTreeView")
        self.setModel(self._fileSystemModel)

        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def _setSignal(self):
        self.doubleClicked.connect(self._openFile)
        self.clicked.connect(lambda: self._fileSystemModel.setReadOnly(True))

        self._contextMenu.openFileSignal.connect(lambda: self._openFile(self._currentClickedIndex))
        self._contextMenu.newFolderSignal.connect(self._createNewFolder)
        self._contextMenu.newFileSignal.connect(self._createNewFile)
        self._contextMenu.renameSignal.connect(self._rename)
        self._contextMenu.deleteSignal.connect(self._delete)
        self._contextMenu.pasteSignal.connect(self._paste)
        self._contextMenu.copySignal.connect(self._copy)
        self._contextMenu.cutSignal.connect(self._cut)

    def _setPath(self, path):
        _index = self._fileSystemModel.setRootPath(path)
        self.setRootIndex(_index)

    def _openFile(self, index):
        if not self._fileSystemModel.isDir(index):
            print("打开")

    def _createNewFolder(self):
        _folderName, _ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称")
        if not _ok:
            return

        _targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
        _targetPath = Path(_targetPath) if _targetPath else Path(self._projectPath)
        _targetPath = (_targetPath / _folderName) if _targetPath.is_dir() else (_targetPath.parent / _folderName)

        if _targetPath.exists():
            QMessageBox.critical(self, '错误', f'{_folderName}已存在')
            return

        _targetPath.mkdir()
        self.update(self._currentClickedIndex)
        self.expand(self._currentClickedIndex)

    def _createNewFile(self, ext):
        _fileName, _ok = QInputDialog.getText(self, "新建文件", "请输入文件名称")
        if not _ok:
            return

        _fileName = f"{_fileName}.{ext}"
        _targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
        _targetPath = Path(_targetPath) if _targetPath else Path(self._projectPath)
        _targetPath = (_targetPath / _fileName) if _targetPath.is_dir() else (_targetPath.parent / _fileName)

        if _targetPath.exists():
            QMessageBox.critical(self, '错误', f'{_fileName}已存在')
            return

        _targetPath.touch()
        self.update(self._currentClickedIndex)
        self.expand(self._currentClickedIndex)

    def _rename(self):
        self._fileSystemModel.setReadOnly(False)
        self.edit(self._currentClickedIndex)

    def _delete(self):
        _choice = QMessageBox.question(self, '删除', '确定要删除吗？', QMessageBox.Yes | QMessageBox.No)

        if _choice == QMessageBox.No:
            return

        for _index in self.selectedIndexes():
            path = Path(self._fileSystemModel.filePath(_index))
            shutil.rmtree(path) if path.is_dir() else path.unlink()
            self.update(_index)

    def _paste(self):
        ...

    def _copy(self):
        ...

    def _cut(self):
        ...

    def contextMenuEvent(self, event):
        _index = self.indexAt(event.pos())
        self._currentClickedIndex = _index

        if not _index.isValid():
            self._contextMenu.execBlankAreaMainMenu(event.globalPos())
            return

        if not self._fileSystemModel.isDir(_index):
            self._contextMenu.execFileMainMenu(event.globalPos())
        else:
            self._contextMenu.execFolderMainMenu(event.globalPos())


class SearchLine(QLineEdit):
    def __init__(self):
        super(SearchLine, self).__init__()

        self._setUI()

    def _setUI(self):
        self._setWindowAttribute()
        self._setSignal()

    def _setWindowAttribute(self):
        self.setObjectName("searchLine")
        self.setPlaceholderText("搜索资源")

    def _setSignal(self):
        self.textChanged.connect(self._search)

    def _search(self, keyword):
        print(keyword)





