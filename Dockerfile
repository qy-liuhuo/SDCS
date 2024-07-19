# 使用Ubuntu 20.04作为基础镜像
FROM ubuntu:20.04


# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip
# 设置工作目录
WORKDIR /app

# 复制应用程序文件到容器
COPY cache.py /app
COPY hash.py /app
COPY server.py /app
COPY requirements.txt /app

# RUN pip install --upgrade pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Python依赖
RUN pip3 install -r requirements.txt


# 暴露端口
EXPOSE 80

CMD ["python3","/app/server.py"]
