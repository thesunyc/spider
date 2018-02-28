#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import sys
sys.path.append('E:\workspace\spider')
from music163.scanner.PageScanner import PageScanner

redisConf = {}
pageScanner = PageScanner(redisConf,enableCache=True)
pageScanner.start('http://music.163.com/discover/toplist?id=3778678')
