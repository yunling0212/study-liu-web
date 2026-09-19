# study-liu Web 版 Dockerfile
# 构建：docker build -t study-liu-web ./backend
# 运行：docker run -d -p 8000:8000 -v studyliu_data:/app/backend/data --name study-liu study-liu-web

FROM python:3.12-slim

WORKDIR /app/backend

# 先装依赖（利用 Docker 层缓存：requirements 不变就不重装）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再拷代码（core/agents/tools/i18n/app + 前端在 compose 里挂载或上下文拷入）
COPY . .

# data 目录做成卷，容器重建数据不丢
VOLUME ["/app/backend/data"]

EXPOSE 8000

# gunicorn 多 worker + uvicorn worker class，2C2G 建议 2 workers
CMD ["gunicorn", "app.main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "300"]
