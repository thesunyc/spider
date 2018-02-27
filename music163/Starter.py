#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import sys
sys.path.append('E:\workspace\spider')
from music163.scanner.PageScanner import PageScanner

redisConf = {"host":"139.196.123.29","password":"redis1qaz2wsx"}
pageScanner = PageScanner(redisConf)
pageScanner.start('http://music.163.com/discover/toplist?id=3778678')
