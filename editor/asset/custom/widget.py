import os
import shutil
import platform
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editor.asset.custom.menu import ProjectTreeViewMenu


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
        self.setObjectName("assetProjectTreeView")
        self.setModel(self._fileSystemModel)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)

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
        index = self._fileSystemModel.setRootPath(path)
        self.setRootIndex(index)

    def _openFile(self, index):
        if not self._fileSystemModel.isDir(index):
            path = self._fileSystemModel.filePath(index)
            os.system(f"open -a Visual\ Studio\ Code.app {self._projectPath} {path}")

    def _createNewFolder(self):
        folderName, ok = QInputDialog.getText(self, "???????????????", "????????????????????????")
        if not ok:
            return

        targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
        targetPath = Path(targetPath) if targetPath else Path(self._projectPath)
        targetPath = (targetPath / folderName) if targetPath.is_dir() else (targetPath.parent / folderName)

        if targetPath.exists():
            QMessageBox.critical(self, '??????', f'{folderName}?????????')
            return

        targetPath.mkdir()
        self.update(self._currentClickedIndex)
        self.expand(self._currentClickedIndex)

    def _createNewFile(self, ext):
        fileName, ok = QInputDialog.getText(self, "????????????", "?????????????????????")
        if not ok:
            return

        targetPath = self._fileSystemModel.filePath(self._currentClickedIndex)
        targetPath = Path(targetPath) if targetPath else Path(self._projectPath)
        fileName = f"{fileName}{ext}" if not fileName.endswith(ext) else fileName
        targetPath = (targetPath / fileName) if targetPath.is_dir() else (targetPath.parent / fileName)

        if targetPath.exists():
            QMessageBox.critical(self, '??????', f'{fileName}?????????')
            return

        targetPath.touch()
        self.update(self._currentClickedIndex)
        self.expand(self._currentClickedIndex)

    def _rename(self):
        self._fileSystemModel.setReadOnly(False)
        self.edit(self._currentClickedIndex)

    def _delete(self):
        choice = QMessageBox.question(self, '??????', '?????????????????????', QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.No:
            return

        for index in self.selectedIndexes():
            try:
                path = Path(self._fileSystemModel.filePath(index))
                shutil.rmtree(path) if path.is_dir() else path.unlink()
            except FileNotFoundError:
                # ??????????????????????????????????????????????????????FileNotFoundError
                # ????????????try-except?????????
                pass

        self.update()

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
        if self._cutIndexSet:
            self._clipboard.clear()
            self._cutIndexSet.clear()

    def _pasteForCopy(self, originalPath, fileOrFolderName, targetPath):
        if not targetPath.exists():
            if originalPath.is_dir():
                shutil.copytree(originalPath, targetPath)
            else:
                shutil.copyfile(originalPath, targetPath)
        else:
            if originalPath.is_dir():
                QMessageBox.critical(self, '??????????????????', f'??????????????????????????????{fileOrFolderName}???', QMessageBox.Ok)
            else:
                choice = QMessageBox.question(self, '???????????????', f'?????????????????????{fileOrFolderName}??????????????????', QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    shutil.copyfile(originalPath, targetPath)

    def _pasteForCut(self, originalPath, fileOrFolderName, targetPath):
        # ???????????????????????????
        # ??????????????????????????????
        if originalPath == targetPath or originalPath == targetPath.parent:
            return

        if not targetPath.exists():
            originalPath.replace(targetPath)
        else:
            if originalPath.is_dir():
                QMessageBox.critical(self, '??????????????????', f'??????????????????????????????{fileOrFolderName}???', QMessageBox.Ok)
            else:
                choice = QMessageBox.question(self, '???????????????', f'?????????????????????{fileOrFolderName}??????????????????', QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    originalPath.replace(targetPath)

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

    def getFilesAndFolders(self):
        filesAndFolders = Path(self._projectPath).rglob("*")
        return filesAndFolders

    def focusInEvent(self, event):
        super(ProjectTreeView, self).focusInEvent(event)
        # ?????????????????????????????????????????????
        # ???????????????????????????????????????
        # ??????????????????????????????????????????????????????
        if not self._clipboard.mimeData().hasUrls():
            self._cutIndexSet.clear()
            return

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dragMoveEvent(self, event):
        ...

    def dropEvent(self, event):
        data = event.mimeData()
        if not data.hasUrls():
            return

        index = self.indexAt(event.pos())
        for url in data.urls():
            originalPath = Path(url.toString().replace('file://', ''))
            fileOrFolderName = originalPath.name

            targetPath = self._fileSystemModel.filePath(index)
            targetPath = Path(targetPath) if targetPath else Path(self._projectPath)
            targetPath = (targetPath / fileOrFolderName) if targetPath.is_dir() else (targetPath.parent / fileOrFolderName)

            self._pasteForCut(originalPath, fileOrFolderName, targetPath)

        self.update()

    def drawRow(self, painter, option, index):
        """???????????????????????????????????????"""
        super(ProjectTreeView, self).drawRow(painter, option, index)
        brush = QBrush(QColor(0, 105, 217, 50))
        pen = QPen(QColor(0, 0, 0, 0))
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

    def _setWindowAttribute(self):
        self.setObjectName("assetSearchLine")
        self.setPlaceholderText("????????????")
        self.setFocusPolicy(Qt.ClickFocus)
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

    def contextMenuEvent(self, event):
        pass


class SearchListView(QListView):
    def __init__(self):
        super(SearchListView, self).__init__()
        self._standardItemModel = QStandardItemModel()
        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setSignal()

    def _setWidget(self):
        self.hide()
        self.setModel(self._standardItemModel)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _setSignal(self):
        self.doubleClicked.connect(self._openFile)

    def _openFile(self, index):
        item = self._standardItemModel.itemFromIndex(index)
        itemPath = item.toolTip()
        if Path(itemPath).is_dir():
            return

        system = platform.system()
        projectPath = Path('.').cwd().parent.parent
        if system == "Darwin":
            os.system(f"open -a Visual\ Studio\ Code.app {projectPath} {itemPath}")
        elif system == "Windows":
            # windows?????????????????????????????????????????????
            ...

    def setResult(self, matchList):
        self._standardItemModel.clear()
        style = QApplication.style()
        for f in matchList:
            icon = style.standardIcon(QStyle.SP_FileIcon) if f.is_file() else style.standardIcon(QStyle.SP_DirIcon)
            item = QStandardItem(icon, str(f.name))
            item.setToolTip(str(f))
            self._standardItemModel.appendRow(item)