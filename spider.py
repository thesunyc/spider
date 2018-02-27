#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from lianjia.service.Scanner import Scanner
import redis
import threading
import random
import math
import numpy
import time
import json

headers = {\
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'\
    ,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'\
    ,'Accept-Encoding':'gzip, deflate'\
    ,'Accept-Language':'zh-CN,zh;q=0.9,zh-TW;q=0.8'\
    ,'Cache-Control':'no-cache'\
    ,'Connection':'keep-alive'\
    ,'Upgrade-Insecure-Requests':'1'\
    }

'''
while True:
    eventObj = {}
    eventObj['mobile'] = str(random.randint(13600000000,13800000000))
    eventObj['channel'] = "zt" if random.randint(0,1) == 1 else "wt"
    eventObj['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    eventRand = random.randint(1,4)
    if eventRand == 1:
        eventObj['event'] = 'rewardGet'
        eventObj['rewardValue'] = random.randint(1,5120)
    elif eventRand == 2:
        eventObj['event'] = 'rewardSet'
        eventObj['rewardSetQuantity'] = random.randint(10,99)
    elif eventRand == 3:
        eventObj['event'] = 'share'
    elif eventRand == 4:
        eventObj['event'] = 'shareGet'
        eventObj['mobileShare'] = str(random.randint(13600000000,13800000000))
        eventObj['rewardValue'] = random.randint(1,5120)
    redisClient.lpush('xcllhb@queue:event',json.dumps(eventObj))
'''
    
redisClient = redis.Redis(host='139.196.23.41',port=19000)

redisClient.set("testkey","testcontent")

redisClient.delete('testlist1000')
redisClient.lpush('testlist1000',range(0,1000))

redisClient.delete('testset1000')
redisClient.sadd('testset1000',range(0,1000))

chktime = int(time.time())
for index in range(0,1000):
    redisClient.get('testkey')
print(int(time.time()) - chktime)
chktime = int(time.time())
for index in range(0,1000):
    redisClient.lrange('testlist1000',0,-1)
print(int(time.time()) - chktime)
chktime = int(time.time())
for index in range(0,1000):
    redisClient.smembers('testset1000')
print(int(time.time()) - chktime)
chktime = int(time.time())
for index in range(0,1000):
    redisClient.sscan('testset1000',0)
print(int(time.time()) - chktime)

'''
for index in range(13800000001,13800001001):
    redisClient.delete("ydhd:ydhd_user_" + str(index) + "_real_name_pass")
    redisClient.set("ydhd:ydhd_user_" + str(index) + "_real_name_pass","real_name_pass_yes")
'''

'''
for index in range(13800000001,13800001001):
    redisClient.delete("xcllhb@ydhd:userInfo_wt_" + str(index)
        ,"xcllhb@ydhd:llfp_wt_" + str(index)
        ,"xcllhb@ydhd:shareRecord_wt_" + str(index))
'''

