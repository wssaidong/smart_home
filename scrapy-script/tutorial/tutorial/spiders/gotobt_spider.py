import scrapy
from kafka import KafkaProducer
import json

#from tutorial.items import RecruitItem

class RecruitSpider(scrapy.spiders.Spider):
    name = "gotobt"
    allowed_domains = ["gotobt.com"]
    start_urls = [
        "http://gotobt.com/s/dy/qs/Index.Html"
    ]
    def parse_detail(self,response):
        item = response.meta['item']
        magnet = response.xpath('//a[@target="_blank" and @href]')[1].xpath('./@href').extract()[0]
        item['magnet'] = magnet
        
        producer = KafkaProducer(bootstrap_servers=["192.168.3.90:9092"])
        producer.send("log-movie", bytes(json.dumps(item,ensure_ascii=False), encoding='utf-8'))
        yield item

    def parse(self, response):
      for sel in response.xpath('//a[@target="_blank" and @href]'):
        name = sel.xpath('./text()').extract()[0]
        detailLink = sel.xpath('./@href').extract()[0]
        detail_url = "http://gotobt.com" + detailLink

        item = {} #RecruitItem()
        item['name']= name
        item['detail_url']= detail_url
        yield scrapy.Request(url=detail_url,callback=self.parse_detail,meta={'item':item})



