# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV MCP_SERVER_NAME=DocumentConverter
ENV MCP_LOG_LEVEL=INFO
ENV MCP_MAX_FILE_SIZE=50MB
ENV MCP_TEMP_DIR=/tmp
ENV MCP_ENABLE_PANDOC=true
ENV MCP_ENABLE_HTTP=true
ENV MCP_HTTP_PORT=8000

# 暴露端口（如果需要HTTP接口）
EXPOSE 8000

# 创建非root用户
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# 启动命令
CMD ["python", "document_converter_mcp.py"]