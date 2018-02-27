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
    def __init__(self):
        self.cacheKeyPrefix = ''
        self.songBucketCount = 0
        self.enableCache = False
        self.redisClient = redis.Redis()
    
    def getCachekey(self,id):
        hashId = int(hashlib.md5(bytes(id,encoding="utf8")).hexdigest(), 16)
        return self.cacheKeyPrefix + str(jump.hash(hashId,self.songBucketCount))
    
    def existCache(self,id):
        if not self.enableCache:
            return False
        cacheKey = self.getCachekey(str(id))
        if self.redisClient.sismember(cacheKey,id):
            return True
        self.redisClient.sadd(cacheKey,id)
    
    def saveItems(self,path,*items):
        if not items:
            return
        tmpContents = ''
        for item in items:
            if item:
                tmpContents = tmpContents + "\n" + item.toString()
        if tmpContents:
            putContent = 'path=' + path + '&content=' + tmpContents.strip("\n")
            self.redisClient.lpush('put_content',putContent)
    
    