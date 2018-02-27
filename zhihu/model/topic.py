#!/usr/bin/env python3
#-*- coding:utf-8 

class Topic:
    def __init__(self,id,name,url):
        self.id = id
        self.name = name
        self.url = url
    
    def toDic(self):
        return self.__dict__.copy()