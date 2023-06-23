# 使用具有 Python 3.10.12 的基礎映像
FROM python:3.10.12

# 設定工作目錄
WORKDIR /app

# 複製你的 FastAPI 應用至容器中的 /app 目錄
COPY ./app /app

# 安裝需要的依賴
RUN pip install --no-cache-dir -r /app/requirements.txt

# 定義容器啟動時執行的命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]