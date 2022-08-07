import shutil
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
        self._cutIndexSet = set()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()
        self._setPath(self._projectPath)

    def _setWidget(self):
        self.setObjectName("projectTreeView")
        self.setModel(self._fileSystemModel)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)

        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
        self.setSelectionMode(QAbstractItemView.MultiSelection)

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
        index = self._fileSystemModel.setRootPath(path)
        self.setRootIndex(index)

    def _openFile(self, index):
        if not self._fileSystemModel.isDir(index):
            print("打开")

    def _createNewFolder(self):
        folderName, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称")
        if not ok:
            return

        targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
        targetPath = Path(targetPath) if targetPath else Path(self._projectPath)
        targetPath = (targetPath / folderName) if targetPath.is_dir() else (targetPath.parent / folderName)

        if targetPath.exists():
            QMessageBox.critical(self, '错误', f'{folderName}已存在')
            return

        targetPath.mkdir()
        self.update(self._currentClickedIndex)
        self.expand(self._currentClickedIndex)

    def _createNewFile(self, ext):
        fileName, ok = QInputDialog.getText(self, "新建文件", "请输入文件名称")
        if not ok:
            return

        fileName = f"{fileName}.{ext}"
        targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
        targetPath = Path(targetPath) if targetPath else Path(self._projectPath)
        targetPath = (targetPath / fileName) if targetPath.is_dir() else (targetPath.parent / fileName)

        if targetPath.exists():
            QMessageBox.critical(self, '错误', f'{fileName}已存在')
            return

        targetPath.touch()
        self.update(self._currentClickedIndex)
        self.expand(self._currentClickedIndex)

    def _rename(self):
        self._fileSystemModel.setReadOnly(False)
        self.edit(self._currentClickedIndex)

    def _delete(self):
        choice = QMessageBox.question(self, '删除', '确定要删除吗？', QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.No:
            return

        for index in self.selectedIndexes():
            path = Path(self._fileSystemModel.filePath(index))
            shutil.rmtree(path) if path.is_dir() else path.unlink()
            self.update(index)

    def _paste(self):
        data = self._clipboard.mimeData()
        if not data.hasUrls():
            return

        for url in data.urls():
            originalPath = Path(url.toString().replace('file://', ''))
            fileOrFolderName = originalPath.name

            targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
            targetPath = Path(targetPath) if targetPath else Path(self._projectPath)
            targetPath = (targetPath / fileOrFolderName) if targetPath.is_dir() else (targetPath.parent / fileOrFolderName)

            if self._cutIndexSet:
                self._pasteForCut(originalPath, fileOrFolderName, targetPath)
            else:
                self._pasteForCopy(originalPath, fileOrFolderName, targetPath)

        self.update()

    def _pasteForCopy(self, originalPath, fileOrFolderName, targetPath):
        if not targetPath.exists():
            if originalPath.is_dir():
                shutil.copytree(originalPath, targetPath)
            else:
                shutil.copyfile(originalPath, targetPath)
        else:
            if originalPath.is_dir():
                QMessageBox.critical(self, '文件夹已存在', f'该目录下已存在文件夹{fileOrFolderName}！', QMessageBox.Ok)
            else:
                choice = QMessageBox.question(self, '文件已存在', f'该目录下已存在{fileOrFolderName}，是否覆盖？', QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    shutil.copyfile(originalPath, targetPath)

    def _pasteForCut(self, originalPath, fileOrFolderName, targetPath):
        if not targetPath.exists():
            originalPath.replace(targetPath)
        else:
            if originalPath.is_dir():
                QMessageBox.critical(self, '文件夹已存在', f'该目录下已存在文件夹{fileOrFolderName}！', QMessageBox.Ok)
            else:
                choice = QMessageBox.question(self, '文件已存在', f'该目录下已存在{fileOrFolderName}，是否覆盖？', QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    originalPath.replace(targetPath)

        self._clipboard.clear()
        self._cutIndexSet.clear()

    def _copy(self):
        urlList = []
        data = QMimeData()
        self._cutIndexSet.clear()

        for index in self.selectedIndexes():
            path = self._fileSystemModel.filePath(index)
            urlList.append(QUrl(path))

        data.setUrls(urlList)
        self.clearSelection()
        self._clipboard.setMimeData(data)

    def _cut(self):
        urlList = []
        data = QMimeData()
        self._cutIndexSet.clear()

        for index in self.selectedIndexes():
            path = self._fileSystemModel.filePath(index)
            urlList.append(QUrl(path))
            self._cutIndexSet.add(index)

        data.setUrls(urlList)
        self.clearSelection()
        self._clipboard.setMimeData(data)

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self._currentClickedIndex = index

        if not index.isValid():
            self._contextMenu.execBlankAreaMainMenu(event.globalPos())
            return

        if not self._fileSystemModel.isDir(index):
            self._contextMenu.execFileMainMenu(event.globalPos())
        else:
            self._contextMenu.execFolderMainMenu(event.globalPos())

    def drawRow(self, painter, option, index):
        super(ProjectTreeView, self).drawRow(painter, option, index)
        brush = QBrush(QColor(0, 105, 217, 50))
        pen = QPen(QColor(0, 105, 217, 50))
        painter.setBrush(brush)
        painter.setPen(pen)

        for cutIndex in self._cutIndexSet:
            if index != cutIndex:
                continue

            x = option.rect.x()
            y = option.rect.y()
            width = option.rect.width()
            height = option.rect.height()
            painter.drawRect(x, y, width, height)


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





