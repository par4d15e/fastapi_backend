# 使用 slim 基础镜像并避免安装仅用于开发的包或创建用户
FROM python:3.14.3-slim-trixie

# 保持 Python 输出不缓存以便日志实时，并设置工作目录
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 先复制项目元数据，这样依赖安装能利用缓存
COPY pyproject.toml README.md ./

# 安装构建所需库和项目依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir .

# 复制应用代码
COPY app ./app
COPY alembic ./alembic

# 开放 uvicorn 使用的端口（可选）
EXPOSE 8000

# 默认启动命令，运行 API 服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

