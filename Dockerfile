FROM python:3.11-slim

WORKDIR /app

# 先拷依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再拷代码
COPY . .

# 非 root 用户运行（安全）
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
    "-w", "4", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "-b", "0.0.0.0:8000", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]