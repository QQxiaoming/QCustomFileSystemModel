# QCustomFileSystemModel

这是一个自定义的文件系统模型，可以用于QTreeView控件。

与QFileSystemModel不同的是，QCustomFileSystemModel可以被继承，可以自定义文件系统模型的数据，而并非本地文件系统。比如，通过SSH连接到远程主机，可以通过QCustomFileSystemModel来显示远程主机的文件系统。