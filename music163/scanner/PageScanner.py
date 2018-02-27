#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import threading
import requests
sys.path.append('E:\workspace\spider')
from lxml import etree
from music163.scanner.SongScanner import SongScanner
from music163.scanner.BaseScanner import BaseScanner
from base.config.Config import COMMON_HEADERS

class PageScanner(BaseScanner):
    def __init__(self,redisConf,enableCache=False):
        self.songScanner = SongScanner(redisConf,enableCache)
        self.threadList = []
        self.enableCache = enableCache
    
    def start(self,*scanPageList):
        for page in scanPageList:
            if self.existCache(page):
                continue
            res = requests.get(page,headers=COMMON_HEADERS)
            if not res or not res.text:
                continue
            doc = etree.HTML(res.text)
            if not doc:
                continue
            pageThread = threading.Thread(target=self.songScanner.scanSong,args=(doc,))
            self.threadList.append(pageThread)
            pageThread.start()
        for thread in self.threadList:
            thread.join()