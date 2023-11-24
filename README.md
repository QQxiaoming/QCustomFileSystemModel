# QCustomFileSystemModel

这是一个自定义的文件系统模型，可以用于QTreeView控件。

与QFileSystemModel不同的是，QCustomFileSystemModel可以被继承，可以自定义文件系统模型的数据，而并非本地文件系统。比如，通过SSH连接到远程主机，可以通过QCustomFileSystemModel来显示远程主机的文件系统。

## 示例 1

- 首先继承QCustomFileSystemModel，定义你需要模型

```cpp
class QCurrentNativeFileSystemModel : public QCustomFileSystemModel
{
    Q_OBJECT
public:
    explicit QNativeFileSystemModel(QObject *parent = 0)
        : QCustomFileSystemModel(parent) {
    }
    ~QNativeFileSystemModel() {
    }

    QString separator() const;
    QStringList pathEntryList(const QString &path);
    void pathInfo(QString path, bool &isDir, uint64_t &size, QDateTime &lastModified);
};
```

- 实现separator函数，返回路径分隔符，示例代码如下：

```cpp
QString QCurrentNativeFileSystemModel::separator() const
{
    return QDir::separator();
}
```

- 实现pathEntryList函数，返回指定路径下的文件列表，示例代码如下：

```cpp
QStringList QCurrentNativeFileSystemModel::pathEntryList(const QString &path)
{
    QDir dir(path);
    return dir.entryList(QDir::AllEntries | QDir::NoDotAndDotDot);
}
```

- 实现pathInfo函数，返回指定路径的文件信息，示例代码如下：

```cpp
void QCurrentNativeFileSystemModel::pathInfo(QString path, bool &isDir, uint64_t &size, QDateTime &lastModified)
{
    QFileInfo info(path);
    isDir = info.isDir();
    size = info.size();
    lastModified = info.lastModified();
}
```

- 在QTreeView中使用QCurrentNativeFileSystemModel，示例代码如下：

```cpp
QTreeView *treeView = new QTreeView(this);
QCurrentNativeFileSystemModel *model = new QCurrentNativeFileSystemModel(this);
treeView->setModel(model);
treeView->setRootIndex(model->setRootPath(QDir::homePath()));
treeView->show();
```

## 示例 2

- 首先继承QCustomFileSystemModel，定义你需要模型

```cpp
class QSSHFileSystemModel : public QCustomFileSystemModel
{
    Q_OBJECT
public:
    explicit QSSHFileSystemModel(QObject *parent = 0)
        : QCustomFileSystemModel(parent) {
    }
    ~QSSHFileSystemModel() {
    }

    QString separator() const;
    QStringList pathEntryList(const QString &path);
    void pathInfo(QString path, bool &isDir, uint64_t &size, QDateTime &lastModified);
};
```

- 实现separator函数，返回路径分隔符，示例代码如下：

```cpp
QString QSSHFileSystemModel::separator() const
{
    return "/";
}
```

- 实现pathEntryList函数，返回指定路径下的文件列表，示例代码如下：

```cpp
QStringList QSSHFileSystemModel::pathEntryList(const QString &path)
{
    QStringList list;
    LIBSSH2_SFTP_HANDLE *sftp_handle = NULL;
    LIBSSH2_SFTP_ATTRIBUTES attrs;
    char buffer[512];
    int rc;
    int i;

    sftp_handle = libssh2_sftp_opendir(sftp_session, path.toUtf8().data());
    if (!sftp_handle) {
        return list;
    }

    do {
        rc = libssh2_sftp_readdir(sftp_handle, buffer, sizeof(buffer), &attrs);
        if (rc > 0) {
            QString name = QString::fromUtf8(buffer);
            if (name != "." && name != "..") {
                list.append(name);
            }
        }
    } while (rc > 0);

    libssh2_sftp_closedir(sftp_handle);

    return list;
}
```

- 实现pathInfo函数，返回指定路径的文件信息，示例代码如下：

```cpp
void QSSHFileSystemModel::pathInfo(QString path, bool &isDir, uint64_t &size, QDateTime &lastModified)
{
    LIBSSH2_SFTP_ATTRIBUTES attrs;
    int rc;

    rc = libssh2_sftp_stat(sftp_session, path.toUtf8().data(), &attrs);
    if (rc == 0) {
        isDir = LIBSSH2_SFTP_S_ISDIR(attrs.permissions);
        size = attrs.filesize;
        lastModified = QDateTime::fromTime_t(attrs.mtime);
    }
}
```

- 在QTreeView中使用QSSHFileSystemModel，示例代码如下：

```cpp
QTreeView *treeView = new QTreeView(this);
QSSHFileSystemModel *model = new QSSHFileSystemModel(this);
treeView->setModel(model);
treeView->setRootIndex(model->setRootPath("/"));
treeView->show();
```

## 示例 3

- 首先继承QCustomFileSystemModel，定义你需要模型

```cpp
class QFTPFileSystemModel : public QCustomFileSystemModel
{
    Q_OBJECT
public:
    explicit QFTPFileSystemModel(QObject *parent = 0)
        : QCustomFileSystemModel(parent) {
    }
    ~QFTPFileSystemModel() {
    }

    QString separator() const;
    QStringList pathEntryList(const QString &path);
    void pathInfo(QString path, bool &isDir, uint64_t &size, QDateTime &lastModified);
};
```

- 实现separator函数，返回路径分隔符，示例代码如下：

```cpp
QString QFTPFileSystemModel::separator() const
{
    return "/";
}
```

- 实现pathEntryList函数，返回指定路径下的文件列表，示例代码如下：

```cpp
QStringList QFTPFileSystemModel::pathEntryList(const QString &path)
{
    QStringList list;
    QUrl url(path);
    QNetworkRequest request(url);
    QNetworkReply *reply = networkAccessManager->get(request);
    QEventLoop loop;
    connect(reply, SIGNAL(finished()), &loop, SLOT(quit()));
    loop.exec();

    if (reply->error() == QNetworkReply::NoError) {
        QDomDocument doc;
        doc.setContent(reply->readAll());
        QDomNodeList nodes = doc.elementsByTagName("a");
        for (int i = 0; i < nodes.size(); i++) {
            QString name = nodes.at(i).toElement().text();
            if (name != "." && name != "..") {
                list.append(name);
            }
        }
    }

    reply->deleteLater();

    return list;
}
```

- 实现pathInfo函数，返回指定路径的文件信息，示例代码如下：

```cpp
void QFTPFileSystemModel::pathInfo(QString path, bool &isDir, uint64_t &size, QDateTime &lastModified)
{
    QUrl url(path);
    QNetworkRequest request(url);
    QNetworkReply *reply = networkAccessManager->head(request);
    QEventLoop loop;
    connect(reply, SIGNAL(finished()), &loop, SLOT(quit()));
    loop.exec();

    if (reply->error() == QNetworkReply::NoError) {
        isDir = reply->hasRawHeader("Content-Type") && reply->rawHeader("Content-Type").startsWith("text/html");
        size = reply->hasRawHeader("Content-Length") ? reply->rawHeader("Content-Length").toULongLong() : 0;
        lastModified = reply->hasRawHeader("Last-Modified") ? QDateTime::fromString(reply->rawHeader("Last-Modified"), "ddd, dd MMM yyyy hh:mm:ss 'GMT'") : QDateTime();
    }

    reply->deleteLater();
}
```

- 在QTreeView中使用QFTPFileSystemModel，示例代码如下：

```cpp
QTreeView *treeView = new QTreeView(this);
QFTPFileSystemModel *model = new QFTPFileSystemModel(this);
treeView->setModel(model);
treeView->setRootIndex(model->setRootPath("ftp://ftp.gnu.org/gnu/"));
treeView->show();
```
