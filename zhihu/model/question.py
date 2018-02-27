#!/usr/bin/env python3
#-*- coding:utf-8 
import json

class Question:
    def __init__(self,id,name,type,url):
        self.id = id
        self.name = name
        self.type = type
        self.url = url
        self.topics = []
        self.commentCount = 0
        self.followCount = 0
        self.visitCount = 0
    
    def toDic(self):
        dic = self.__dict__.copy()
        dic['topics'] = []
        for topic in self.topics:
            dic['topics'].append(topic.toDic())
        return dic
    
    def toString(self):
        return json.dumps(self.toDic(),ensure_ascii=False)