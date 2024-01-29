# -*- coding: utf-8 -*-
# This file is part of the https://github.com/QQxiaoming/QCustomFileSystemModel.git
# project.
# 
# Copyright (C) 2023 Quard <2014500726@smail.xtu.edu.cn>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
from PySide6.QtCore import (QAbstractItemModel, QFileInfo, QDir, QModelIndex, Qt, Signal, Slot)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

class QCustomFileSystemItem(object):
    def __init__(self, path, parent=None):
        super(QCustomFileSystemItem, self).__init__()
        self.m_path = path
        self.m_parentItem = parent
        self.m_childItems = []
        self.m_size = 0
        self.m_lastModified = None
        self.m_isDir = False

    def appendChild(self, child):
        self.m_childItems.append(child)

    def removeChild(self, row):
        self.m_childItems.pop(row)

    def removeChildren(self):
        self.m_childItems = []

    def child(self, row):
        return self.m_childItems[row]

    def childCount(self):
        return len(self.m_childItems)

    def columnCount(self):
        return 4

    def data(self):
        return self.m_path

    def row(self):
        if self.m_parentItem:
            return self.m_parentItem.m_childItems.index(self)
        return 0

    def setSize(self, size):
        self.m_size = size

    def size(self):
        return self.m_size

    def setLastModified(self, lastModified):
        self.m_lastModified = lastModified

    def lastModified(self):
        return self.m_lastModified

    def setIsDir(self, isDir):
        self.m_isDir = isDir

    def isDir(self):
        return self.m_isDir

    def parent(self):
        return self.m_parentItem

class QCustomFileSystemModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(QCustomFileSystemModel, self).__init__(parent)
        self.m_rootItem = None
        self.m_rootPath = ""

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parentItem = None
        if not parent.isValid():
            parentItem = self.m_rootItem
        else:
            parentItem = parent.internalPointer()
        if parentItem is None:
            return QModelIndex()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()
        childItem = child.internalPointer()
        parentItem = childItem.parent()
        if parentItem is None:
            return QModelIndex()
        if parentItem == self.m_rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.m_rootItem
        else:
            parentItem = parent.internalPointer()
        if parentItem is None:
            return 0
        return parentItem.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            if self.m_rootItem is None:
                return 0
            return self.m_rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole and role != Qt.DecorationRole:
            return None
        item = index.internalPointer()
        if item.data() == "":
            return None
        if role == Qt.DecorationRole and index.column() == 0:
            if item.isDir():
                return QIcon.fromTheme("folder")
            else:
                return QIcon.fromTheme("text-x-generic")
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.data().split(self.separator())[-1]
            elif index.column() == 1:
                return "Directory" if item.isDir() else "File"
            elif index.column() == 2:
                if item.isDir():
                    if item.childCount() == 1 and item.child(0).data() == "":
                        return "Loading..."
                    else:
                        return str(item.childCount())
                else:
                    if item.size() <= 1024:
                        return str(item.size()) + " B"
                    elif item.size() <= 1024 * 1024:
                        return str(round(item.size() / 1024.0, 2)) + " KB"
                    elif item.size() <= 1024 * 1024 * 1024:
                        return str(round(item.size() / (1024.0 * 1024.0), 2)) + " MB"
                    else:
                        return str(round(item.size() / (1024.0 * 1024.0 * 1024.0), 2)) + " GB"
            elif index.column() == 3:
                if item.lastModified() is None:
                    return ""
                else:
                    return item.lastModified().toString("yyyy-MM-dd hh:mm:ss")
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Type"
            elif section == 2:
                return "Size"
            elif section == 3:
                return "Last Modified"
        return None

    def fetchMore(self, parent):
        if not parent.isValid():
            return
        parentItem = parent.internalPointer()
        if parentItem.childCount() != 1:
            return
        if parentItem.child(0).data() != "":
            return
        entries = self.pathEntryList(parentItem.data())
        if len(entries) == 0:
            return
        #remove dummy item
        parentItem.removeChild(0)
        dirItems = []
        fileItems = []
        for entry in entries:
            childPath = parentItem.data() + self.separator() + entry
            childItem = QCustomFileSystemItem(childPath, parentItem)
            isDir, size, lastModified = self.pathInfo(childPath)
            childItem.setIsDir(isDir)
            childItem.setLastModified(lastModified)
            if isDir:
                dirItems.append(childItem)
                #add dummy item
                dummyItem = QCustomFileSystemItem("", childItem)
                childItem.appendChild(dummyItem)
            else:
                childItem.setSize(size)
                fileItems.append(childItem)
        for item in dirItems:
            parentItem.appendChild(item)
        for item in fileItems:
            parentItem.appendChild(item)

    def canFetchMore(self, parent):
        if not parent.isValid():
            return False
        parentItem = parent.internalPointer()
        if parentItem.childCount() != 1:
            return False
        if parentItem.child(0).data() != "":
            return False
        return True

    def setRootPath(self, path):
        self.beginResetModel()
        self.m_rootItem = QCustomFileSystemItem(path)
        self.m_rootPath = path
        rootEntries = self.pathEntryList(self.m_rootPath)
        dirItems = []
        fileItems = []
        for entry in rootEntries:
            childPath = self.separator() + entry
            if path != self.separator():
                childPath = path + childPath
            childItem = QCustomFileSystemItem(childPath, self.m_rootItem)
            isDir, size, lastModified = self.pathInfo(childPath)
            childItem.setIsDir(isDir)
            childItem.setLastModified(lastModified)
            if isDir:
                dirItems.append(childItem)
                #add dummy item
                dummyItem = QCustomFileSystemItem("", childItem)
                childItem.appendChild(dummyItem)
            else:
                childItem.setSize(size)
                fileItems.append(childItem)
        for item in dirItems:
            self.m_rootItem.appendChild(item)
        for item in fileItems:
            self.m_rootItem.appendChild(item)
        self.endResetModel()
        return self.createIndex(0, 0, self.m_rootItem)

    def rootPath(self):
        return self.m_rootPath

    def filePath(self, index):
        if not index.isValid():
            return ""
        item = index.internalPointer()
        return item.data()

    def refresh(self, index):
        if not index.isValid():
            return
        item = index.internalPointer()
        if item.childCount() == 1 and item.child(0).data() == "":
            return
        self.beginResetModel()
        item.removeChildren()
        dummyItem = QCustomFileSystemItem("", item)
        item.appendChild(dummyItem)
        self.fetchMore(index)
        self.endResetModel()

class QNativeFileSystemModel(QCustomFileSystemModel):
    def __init__(self, parent=None):
        super(QNativeFileSystemModel, self).__init__(parent)
        self.m_hideFiles = False

    def separator(self):
        return QDir.separator()

    def pathEntryList(self, path):
        #qdir = QDir(path)
        #return qdir.entryList(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden)
        # note: QDir.entryList() is issued in pyside6, we shuold use python os.listdir() instead
        import os
        dir_list = os.listdir(path)
        # remove . and ..
        for item in dir_list:
            if item == '.' or item == '..':
                dir_list.remove(item)
        if not self.m_hideFiles:
            # remove hidden files
            remove_list = []
            for item in dir_list:
                if item.startswith('.'):
                    continue
                remove_list.append(item)
            return remove_list
        else:
            return dir_list

    def pathInfo(self, path):
        qdir = QFileInfo(path)
        isDir = qdir.isDir()
        size = qdir.size()
        lastModified = qdir.lastModified()
        return isDir, size, lastModified

    def setHideFiles(self, enable):
        self.m_hideFiles = enable

    def hideFiles(self):
        return self.m_hideFiles

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QTreeView, QMenu
    from PySide6.QtCore import QObject, SIGNAL, SLOT, QFileInfo, QFile, QIODevice, QPoint
    app = QApplication(sys.argv)
    view = QTreeView()
    fileSystemModel = QNativeFileSystemModel(view)
    view.setModel(fileSystemModel)
    view.setColumnWidth(0, 200)
    view.setColumnWidth(1, 60)
    view.setColumnWidth(2, 100)
    view.setColumnWidth(3, 100)
    view.setRootIndex(fileSystemModel.setRootPath(QDir.homePath()))
    view.resize(640, 480)
    view.setContextMenuPolicy(Qt.CustomContextMenu)
    def showContextMenu(point):
        menu = QMenu(view)
        index = view.indexAt(point)
        if index.isValid():
            def newFolder(index):
                path = fileSystemModel.filePath(index)
                info = QFileInfo(path)
                if not info.isDir():
                    path = info.dir().path()
                    dir = QDir(path)
                    dir.mkdir("New Folder")
                    fileSystemModel.refresh(index.parent())
                else:
                    dir = QDir(path)
                    dir.mkdir("New Folder")
                    fileSystemModel.refresh(index)
            menu.addAction("New Folder", lambda: newFolder(index))
            def newFile(index):
                path = fileSystemModel.filePath(index)
                info = QFileInfo(path)
                if not info.isDir():
                    path = info.dir().path()
                    file = QFile(path + "/New File")
                    file.open(QIODevice.WriteOnly)
                    file.close()
                    fileSystemModel.refresh(index.parent())
                else:
                    file = QFile(path + "/New File")
                    file.open(QIODevice.WriteOnly)
                    file.close()
                    fileSystemModel.refresh(index)
            menu.addAction("New File", lambda: newFile(index))
            menu.addSeparator()
            def delete(index):
                path = fileSystemModel.filePath(index)
                info = QFileInfo(path)
                if info.isDir():
                    dir = QDir(path)
                    dir.removeRecursively()
                else:
                    file = QFile(path)
                    file.remove()
                fileSystemModel.refresh(index.parent())
            menu.addAction("Delete", lambda: delete(index))
        if menu.isEmpty():
            del menu
            return
        menu.move(view.mapToGlobal(point) + QPoint(5, 5))
        menu.show()
    QObject.connect(view, SIGNAL("customContextMenuRequested(const QPoint&)"), showContextMenu)
    view.show()
    sys.exit(app.exec())
