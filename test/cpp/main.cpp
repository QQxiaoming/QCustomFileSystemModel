
#include <QApplication>
#include <QTreeView>
#include <QDir>

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
    view.show();
    return a.exec();
}
