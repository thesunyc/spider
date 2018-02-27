#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json

class Comment:
    def __init__(self,id,userId,songId,content,likedCount,time):
        self.id = id
        self.userId = userId
        self.songId = songId
        self.content = content
        self.likedCount = likedCount
        self.time = time
    
    def toDic(self):
        dic = self.__dict__.copy()
        return dic
    
    def toString(self):
        return json.dumps(self.toDic(),ensure_ascii=False)