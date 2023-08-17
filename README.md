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
docker run -d   --name=zookeeper  \
 -p 2181:2181 \
 -e ZOOKEEPER_CLIENT_PORT=2181  \
confluentinc/cp-zookeeper:latest

docker run -d \
    --name=kafka \
    -p 9092:9092 \
    -e KAFKA_BROKER_ID=0 \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://192.168.3.90:9092 \
    -e KAFKA_LISTENERS=PLAINTEXT://:9092 \
    -e KAFKA_ZOOKEEPER_CONNECT=192.168.3.90:2181 \
    -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
    -e ALLOW_PLAINTEXT_LISTENER=yes \
    wurstmeister/kafka:2.13-2.7.2

docker run -d --name logstash  \
-v /apps/logstash-config-dir/logstash-kafka.conf:/usr/share/logstash/pipeline/logstash.conf \
logstash:7.6.0


docker run -d \
--name elasticsearch_container \
-p 9200:9200 -p 9300:9300  \
docker.elastic.co/elasticsearch/elasticsearch:7.12.0

```

#### 部署scrapy爬虫

通过scrapy-docker构建运行进行镜像

### 下载通知

使用 [pushdeer](http://www.pushdeer.com) 进行下载消息推送