import uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8903, reload=True, log_config="uvicorn_loggin_config.json")

# 1. 初始化 Aerich
#     运行以下命令来初始化 Aerich：
#     aerich init -t app.config.TORTOISE_ORM
#     这会生成一个 aerich.ini 文件和一个 migrations 文件夹。
# 2. 初始化数据库
#     运行以下命令来初始化数据库：
#     aerich init-db
# 3. 生成和应用迁移
#     修改数据模型后，运行以下命令来生成迁移文件：
#     aerich migrate
#     然后应用迁移：
#     aerich upgrade
