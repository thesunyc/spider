#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json

class Song:
    def __init__(self,id=0,title='',artists=[],album={},commentCount=0):
        self.id = id
        self.title = title
        self.artists = artists
        self.album = album
        self.commentCount = commentCount
    
    def toDic(self):
        dic = self.__dict__.copy()
        return dic
    
    def toString(self):
        return json.dumps(self.toDic(),ensure_ascii=False)