#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json

class House:
    def __init__(self,id,cityCode,price,bedroomCount,livingroomCount,bathroomCount
    ,structionArea,floor,orientation,subway,buildTime
    ,longitude,latitude,district,address,community):
        self.id = id
        self.price = price
        self.cityCode = cityCode
        self.bedroomCount = bedroomCount
        self.livingroomCount = livingroomCount
        self.bathroomCount = bathroomCount
        self.structionArea = structionArea
        self.floor = floor
        self.orientation = orientation
        self.subway = subway
        self.buildTime = buildTime
        self.longitude = longitude
        self.latitude = latitude
        self.district = district
        self.address = address
        self.community = community
    
    def toDic(self):
        dic = self.__dict__.copy()
        return dic
    
    def toString(self):
        return json.dumps(self.toDic(),ensure_ascii=False)