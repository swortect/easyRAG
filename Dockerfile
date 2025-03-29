# 使用官方提供的 Python 3.11.9 Alpine Linux 镜像
FROM python:3.11.9-alpine

# 设置环境变量，指定时区为 Asia/Shanghai
ENV TZ=Asia/Shanghai

# 更新 Alpine Linux 的 package lists 并安装必要的工具及依赖
RUN set -ex \
    && apk update \
    && apk add --no-cache --upgrade apk-tools \
    && apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && apk del tzdata \
    && rm -rf /var/cache/apk/*

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器的/app目录下
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8903", "--reload", "--log-config", "uvicorn_loggin_config.json"]