# 1. 选择一个基础镜像
FROM python:3.9-slim-bullseye

# 2. 设置工作目录
WORKDIR /app

# 3. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. 复制并安装依赖
# 这一步在构建镜像时执行，之后除非 requirements.txt 变化，否则不会重跑
COPY requirements.txt .
RUN pip install --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

# 5. 复制你的应用代码 (注意！)
# 即使我们等下要挂载代码，这里也复制一份。
# 这样做的好处是，即使不挂载 volume，这个镜像本身也是一个完整的、可独立运行的应用。
COPY ./backend ./backend

# 6. 声明容器对外暴露的端口
# Gunicorn 将在这个端口上运行，供 Nginx 访问
EXPOSE 5000

# 7. 定义容器启动时执行的命令
# 这个 CMD 会被 docker-compose.yml 中的 command 覆盖，但写上是个好习惯
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "backend:create_app('dev')"]
