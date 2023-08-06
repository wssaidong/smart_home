#!/bin/bash
cd /apps/code/dyzz_spider
docker run --name scrapy --rm -v $(pwd)/tutorial:/runtime/app cai/scrapy scrapy crawl dyzz
