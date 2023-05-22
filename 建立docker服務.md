# 建立Dockerfile

```shell
# 從Python 3.10基礎鏡像開始
FROM python:3.10

# 設置工作目錄
WORKDIR /app

# 複製requirements.txt到工作目錄並安裝依賴項
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用文件到工作目錄
COPY ./backend /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

# 建立image

```shell
docker build -t cbp-backend .
```

# 啟動服務

```shell
docker run -d --name cbp-backend -p 80:8000 -p 33061:33061 cbp-backend
```

# 檢查log

```shell
docker logs -f cbp-backend  # -f: follow -> 顯示最新的log
docker logs cbp-backend
```