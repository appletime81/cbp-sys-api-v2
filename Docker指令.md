# Docker 指令

### 查看log

* sudo docker logs CONTAINER_ID

```shell
sudo docker logs c53a2aea4dbda84f3d1e5f1fb47e8fdd3954d8ec524bf2659c564144c424346d
```

### 查看所有image資訊

```shell
sudo docker image ls
```

### 查看所有coontainer資訊

```shell
sudo docker ps -a
```

* -a: 包含未被執行的container

### 執行container指令

* -d: 背景執行
* -p: 要開啟的port
* appletime81/cbp-sys-api-v2: REPOSITORY名稱(container名稱)
* 第一個8000: container的port
* 第二個8000: host的port

```shell
sudo docker run -d -p 8000:8000 appletime81/cbp-sys-api-v2
```

