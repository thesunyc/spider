#!/usr/bin/env python3
#-*- coding:utf-8 

import jieba
import sys
import json

for line in sys.stdin:
    lineDic = json.loads(line.strip())
    words = jieba.cut(lineDic['name'], cut_all=False)
    print('$$DATA=' + '\t'.join(words))