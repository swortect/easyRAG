### PostgreSQL 和 pgvectorPostgreSQL 是与 MySQL 齐名的开源关系数据库。
- PostgreSQL 默认是不支持存储向量的。
- 只有安装了 pgvector 插件之后，PostgreSQL 才能支持存储向量，才能变成向量数据库。
- 安装 pgvector安装 pgvector 的方式有好几种，最快的方式是使用 docker 安装。

首先我们需要安装 docker。
安装完 docker 之后，我们打开命令行工具，运行以下命令：
```bash
docker pull pgvector/pgvector:pg16
```
这条命令会从 Docker Hub 下载 pgvector 的最新版本（对应 PostgreSQL 16 版本）的镜像。如果你需要其他版本的 PostgreSQL，可以通过更改镜像标签来拉取相应的版本。运行 pgvector拉取完镜像后，我们就可以运行 pgvector 的容器了。
## 在命令行工具中运行以下命令：
```bash
docker run --name pgvector --restart=always -e POSTGRES_USER=pgvector -e POSTGRES_PASSWORD=youpassword -v D:\dockermount\pgvector\pgdata⁠:/var/lib/postgresql/data -p 5432:5432 -d pgvector/pgvector:pg16
```
你可能要根据你的实际情况修改以上命令中的具体参数值：
- –name：容器的名称。
- -e POSTGRES_USER：PostgreSQL 的用户名，以后登录数据库时要使用它。
- -e POSTGRES_PASSWORD：PostgreSQL 的密码，以后登录数据库时要使用它。
- -v：冒号前面的值是 Windows 宿主机里你想要保存数据库数据的目录，冒号后面的值是容器的数据目录。
- 以上示例中的值是将容器的数据目录映射到了你的 Windows 宿主机的 D:\dockermount\pgvector\pgdata 目录。一般来说，你需要将冒号前面的
值修改为 Windows 宿主机你想要保存数据库数据的目录。
- -p：PostgreSQL 的端口。如果你的 Windows 宿主机没有安装 PostgreSQL，则不需要修改
