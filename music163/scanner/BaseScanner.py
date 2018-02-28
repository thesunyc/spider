#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import requests
import json
import redis
import threading
import base64
import jump
import hashlib

class BaseScanner:
    def __init__(self,redisConf):
        self.initCache('',0,False)
        self.redisClient = redis.Redis(redisConf)
    
    def initRedis(self,redisConf):
        self.redisClient = redis.Redis(host=redisConf['host'],password=redisConf['password'])
    
    def initCache(self,cacheKeyPrefix,bucketCount,enableCache):
        self.cacheKeyPrefix = cacheKeyPrefix
        self.bucketCount = bucketCount
        self.enableCache = enableCache
    
    def getCachekey(self,id):
        hashId = int(hashlib.md5(bytes(id,encoding="utf8")).hexdigest(), 16)
        return self.cacheKeyPrefix + str(jump.hash(hashId,self.bucketCount))
    
    def existCache(self,id):
        if not self.enableCache:
            return False
        cacheKey = self.getCachekey(str(id))
        if self.redisClient.sismember(cacheKey,id):
            return True
        self.redisClient.sadd(cacheKey,id)
        print('cache key:' + cacheKey + '=' + id)

    def saveItem(self,path,item):
        if not item:
            return
        putContent = 'path=' + path + '&content=' + item.toString().strip("\n")
        self.redisClient.lpush('put_content',putContent)
    
    def saveItems(self,path,items):
        if not items:
            return
        tmpContents = ''
        for item in items:
            if item:
                tmpContents = tmpContents + "\n" + item.toString()
        if tmpContents:
            putContent = 'path=' + path + '&content=' + tmpContents.strip("\n")
            self.redisClient.lpush('put_content',putContent)
    
    