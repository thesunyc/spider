#!/usr/bin/env python3
#-*- coding:utf-8 
import json

class Author:
    def __init__(self,id,name,headline,gender,isOrg):
        self.id = id
        self.name = name
        self.headline = headline
        self.gender = gender
        self.isOrg = isOrg
    
    def toDic(self):
        dic = self.__dict__.copy()
        return dic