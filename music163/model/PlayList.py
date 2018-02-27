#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json

class PlayList:
    def __init__(self,id,user,title,tags,songIds):
        self.id = id
        self.user = user
        self.title = title
        self.tags = tags
        self.songIds = songIds
    
    def toDic(self):
        dic = self.__dict__.copy()
        return dic
    
    def toString(self):
        return json.dumps(self.toDic(),ensure_ascii=False)