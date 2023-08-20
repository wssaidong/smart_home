# smart_home

## NAS

### 电影爬虫

#### 部署 aria2 下载器

```

docker run -d \
--name aria2-pro-container \
-p 6800:6800 -p 6881-6889:6881-6889/udp \
-v /path/to/your/downloads:/downloads \
p3terx/aria2-pro

```

### 部署 aria2 web界面

```
docker run -d \
--name ariang-container \
-p 8080:8080 
p3terx/ariang

```

#### 部署ELK 记录电影信息

```
cd docker 

docker compose up -d
```

#### 部署scrapy爬虫

通过scrapy-docker构建运行进行镜像

### 下载通知

使用 [pushdeer](http://www.pushdeer.com) 进行下载消息推送