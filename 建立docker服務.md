# 把包Docker

### Step1. 建立Dockerfile

### Step2. 建立docker image

```shell
cd /path/to/Dockerfile

# "image name" = "repository name:tag"
# example: cbps-backend:2023070X
sudo docker build -t "image name" .
```

### 打包container

```shell
sudo docker save "image name" > "file_name.tar"
```
### Load container

```shell
sudo docker load < "file_name.tar"
```

### Step3. 建立docker container

```shell
# "container name" = "image name"
# example: cbps-backend:2023070X
# example: sudo docker run -d -p 8000:80 cbps-backend:2023070X
sudo docker run -d -p 8000:80 'container name'
```

### Step4. 查看container資訊

```shell
sudo docker ps -a
```

or

```shell
sudo docker container ls -a
```