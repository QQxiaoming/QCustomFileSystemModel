
#include <QApplication>
#include <QTreeView>
#include <QDir>
#include <QMenu>

#include "qcustomfilesystemmodel.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QTreeView view;
    QNativeFileSystemModel *fileSystemModel = new QNativeFileSystemModel(&view);
    view.setModel(fileSystemModel);
    view.setColumnWidth(0, 200);
    view.setColumnWidth(1, 60);
    view.setColumnWidth(2, 100);
    view.setColumnWidth(3, 100);
    view.setRootIndex(fileSystemModel->setRootPath(QDir::homePath()));
    view.resize(640, 480);
    view.setContextMenuPolicy(Qt::CustomContextMenu);
    QObject::connect(&view, &QTreeView::customContextMenuRequested, &view, [&](const QPoint &pos){
        QMenu *menu = new QMenu(&view);
        QModelIndex index = view.indexAt(pos);
        if (index.isValid()) {
            menu->addAction("New Folder", [=](){
                QString path = fileSystemModel->filePath(index);
                QFileInfo info(path);
                if (!info.isDir()) {
                    path = info.dir().path();
                    QDir dir(path);
                    dir.mkdir("New Folder");
                    fileSystemModel->refresh(index.parent());
                } else {
                    QDir dir(path);
                    dir.mkdir("New Folder");
                    fileSystemModel->refresh(index);
                }
            });
            menu->addAction("New File", [=](){
                QString path = fileSystemModel->filePath(index);
                QFileInfo info(path);
                if (!info.isDir()) {
                    path = info.dir().path();
                    QFile file(path+"/New File");
                    file.open(QIODevice::WriteOnly);
                    file.close();
                    fileSystemModel->refresh(index.parent());
                } else {
                    QFile file(path+"/New File");
                    file.open(QIODevice::WriteOnly);
                    file.close();
                    fileSystemModel->refresh(index);
                }
            });
            menu->addSeparator();
            menu->addAction("Delete", [=](){
                QString path = fileSystemModel->filePath(index);
                QFileInfo info(path);
                if (info.isDir()) {
                    QDir dir(path);
                    dir.removeRecursively();
                } else {
                    QFile file(path);
                    file.remove();
                }
                fileSystemModel->refresh(index.parent());
            });
        }
        if(menu->isEmpty()) {
            delete menu;
            return;
        }
        menu->move(view.mapToGlobal(pos)+QPoint(5, 5));
        menu->show();
    });
    view.show();
    return a.exec();
}
