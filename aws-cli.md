# AWS CLI

## 複製檔案

```shell
aws s3 cp s3://cht-deploy-bucket-1/backend.tar.gz .
aws s3 cp s3://cht-deploy-bucket-1/frontend.tar.gz .
```

---

## 壓縮

```shell
tar -zcvf ./backend.tar.gz .
tar -zcvf ./frontend.tar.gz .
```

---

## 解壓縮

```shell
tar -zxvf ./backend.tar.gz
tar -zxvf ./frontend.tar.gz
```