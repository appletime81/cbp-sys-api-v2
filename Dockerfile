# Install Python 3.10.11 的基礎映像
FROM python:3.10.11

# 設定工作目錄
WORKDIR /app

# 複製你的 FastAPI 應用至容器中的 /app 目錄
COPY . /app

# 升級pip
RUN pip install --upgrade pip

# 安裝需要的依賴
RUN pip install --no-cache-dir -r ./requirements.txt

# 安裝 nginx, awscli
RUN apt-get update && apt-get install -y nginx && apt-get install -y awscli

# 複製 Nginx 配置至容器中的 /etc/nginx/conf.d/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 刪除默認的 Nginx 配置
RUN rm /etc/nginx/sites-enabled/default

# 定義容器啟動時執行的命令
CMD service nginx start & uvicorn main:app --host 0.0.0.0 --port 8000 & wait