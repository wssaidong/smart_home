
from urllib import request
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import json
from aria2 import PyAria2

from kafka import KafkaConsumer

headers = {
    'Content-Type': 'application/json'
}

def searchEs(movie):
    defaultHost = "http://192.168.3.90:9200"
    searchUrl = defaultHost + '/_search'
    queryDatas = {
    "query": {
        "bool": {
        "must": [],
        "filter": [
            {
            "bool": {
                "should": [
                {
                    "match_phrase": {
                    }
                }
                ],
                "minimum_should_match": 1
            }
            },
            {
            "range": {
                "@timestamp": {
                "format": "strict_date_optional_time",
                }
            }
            }
        ],
        "should": [],
        "must_not": []
        }
    }
    }

    utc_zero = datetime.now(timezone.utc)
    utz_zero_pass = utc_zero - timedelta(days=365)
    utz_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    end = utc_zero.strftime(utz_format)
    before = utz_zero_pass.strftime(utz_format)

    queryDatas["query"]["bool"]["filter"][1]["range"]["@timestamp"]['gte'] = before
    queryDatas["query"]["bool"]["filter"][1]["range"]["@timestamp"]['lte'] = end
    queryDatas["query"]["bool"]["filter"][0]["bool"]["should"][0]["match_phrase"]['name'] = movie


    reqDatasStr = json.dumps(queryDatas)
    req = request.Request(url = searchUrl, data = reqDatasStr.encode(encoding='utf-8'), method = 'GET', headers = headers)
    resp = request.urlopen(req)
    respData = json.loads(resp.read().decode('utf-8'))
    total = respData['hits']['total']['value']
    return total

consumer = KafkaConsumer('log-movie',group_id='log-movie-consumer',bootstrap_servers=['192.168.3.90:9092'])
for message in consumer:
    movieInfo = json.loads(message.value.decode('utf-8'))
    num = searchEs(movieInfo['name'])
    if(num == 0):
        print('download:', movieInfo['name'])
        pyAria2 = PyAria2(secret='prc_password')
        pyAria2.addUri(uris = movieInfo['magnet'], position= {"dir":"/downloads"})

