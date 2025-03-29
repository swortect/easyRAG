from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取数据库配置
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": DATABASE_NAME,
                "host": DATABASE_HOST,
                "password": DATABASE_PASSWORD,
                "port": DATABASE_PORT,
                "user": DATABASE_USER,
            },
            "pool_size": 10,  # 设置连接池大小为 10
            "max_overflow": 5,  # 最大溢出连接数
            "pool_recycle": 1800,  # 连接回收时间
        },
        "search": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": DATABASE_NAME,
                "host": DATABASE_HOST,
                "password": DATABASE_PASSWORD,
                "port": DATABASE_PORT,
                "user": DATABASE_USER,
            },
            "pool_size": 10,  # 设置连接池大小为 10
            "max_overflow": 5,  # 最大溢出连接数
            "pool_recycle": 1800,  # 连接回收时间
        }
    },
    "apps": {
        "models": {
            # "models": ["app.models", "aerich.models"],
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC",
}