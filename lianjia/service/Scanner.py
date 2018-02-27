#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import sys
sys.path.append('E:\workspace\spider')
import redis
import requests
from lxml import etree
from lianjia.model.House import House
import traceback
import os

class Scanner:
    def __init__(self,accessToken,headers={},houseFilename='/lianjia/house.json',redisHost='139.196.123.29',redisPassword='redis1qaz2wsx'):
        self.headers = headers
        self.accessToken = accessToken
        self.houseFilename = houseFilename
        self.redisHost = redisHost
        self.redisPassword = redisPassword
        self.redisClient = redis.Redis(host=self.redisHost,password=self.redisPassword)
        self.redisClient.keys('yxllhb@user*')
        self.houses = []
    
    def scanSecondHandHouse(self,saveHouse=False,startOffset=1,maxOffset=100):
        hostUrl = 'http://sh.lianjia.com'
        offset = startOffset
        requestErrCount = 0
        while True:
            res = requests.get(hostUrl + '/ershoufang/d' + str(offset),headers=self.headers)
            if not res or not res.text:
                break
            doc = etree.HTML(res.text)
            houseLinks = doc.xpath('//ul[@class="js_fang_list"]/li/a')
            if not houseLinks or len(houseLinks)<=0:
                break
            for houseLink in houseLinks:
                houseHref = houseLink.get('href')
                try:
                    houseRes = requests.get(hostUrl + houseHref,headers=self.headers)
                except:
                    traceback.print_exc()
                    requestErrCount += 1
                    if requestErrCount >= 6:
                        os._exit()
                    continue
                if houseRes and houseRes.text:
                    try:
                        houseDoc = etree.HTML(houseRes.text)
                        houseId = houseDoc.xpath('//span[text()="房源编号"]/following-sibling::span[1]')[0].text.strip('"').strip()
                        price = int(houseDoc.xpath('//span[@class="price-num"]')[0].text)
                        roomInfo = houseDoc.xpath('//span[text()="房屋户型"]/following-sibling::span[1]')[0].text
                        bedroomCount = int(roomInfo[0:roomInfo.index('室')])
                        livingroomCount = int(roomInfo[roomInfo.index('厅')-1:roomInfo.index('厅')])
                        bathroomCount = int(roomInfo[roomInfo.index('卫')-1:roomInfo.index('卫')])
                        structionArea = float(houseDoc.xpath('//span[text()="建筑面积"]/following-sibling::span[1]')[0].text[:-1])
                        floorInfo = houseDoc.xpath('//span[text()="所在楼层"]/following-sibling::span[1]')[0].text
                        floor = int(floorInfo[floorInfo.index('层')-1:floorInfo.index('层')])
                        orientationInfo = houseDoc.xpath('//span[text()="房屋朝向"]/following-sibling::span[1]')
                        if orientationInfo and len(orientationInfo)>0:
                            orientation = houseDoc.xpath('//span[text()="房屋朝向"]/following-sibling::span[1]')[0].text.strip()
                        else:
                            orientation = ''
                        if houseDoc.xpath('//span[text()="地铁房"]'):
                            subway = True
                        else:
                            subway = False
                        buildTimeInfo = houseDoc.xpath('//span[text()="建筑年代"]/following-sibling::span[1]')[0].text.strip('"').strip()
                        try:
                            buildTimeIndex = buildTimeInfo.index('年')
                            buildTime = int(buildTimeInfo[buildTimeIndex-4:buildTimeIndex]) if buildTimeIndex else 0
                        except:
                            buildTime = 0
                        mapDiv = houseDoc.xpath('//div[@id="aroundApp"]')[0]
                        longitude = float(mapDiv.get('longitude'))
                        latitude = float(mapDiv.get('latitude'))
                        community = mapDiv.get('xiaoqu')
                        districtLinks = houseDoc.xpath('//span[@class="maininfo-estate-name"]/a')
                        district = ''
                        for districtLink in districtLinks[1:]:
                            district = district + '/' + districtLink.text
                        district = district.strip('/')
                        address = houseDoc.xpath('//span[@class="item-cell maininfo-estate-address"]')[0].text
                        house = House(id=houseId,cityCode='sh',price=price,bedroomCount=bedroomCount,livingroomCount=livingroomCount,bathroomCount=bathroomCount
                        ,structionArea=structionArea,floor=floor,orientation=orientation,subway=subway,buildTime=buildTime
                        ,longitude=longitude,latitude=latitude,district=district,address=address,community=community)
                        self.putHouse(house,saveHouse=saveHouse)
                    except:
                        print("exception href=" + houseHref)
                        traceback.print_exc()
            offset += 1
            if offset >= maxOffset:
                break
        if saveHouse:
            self.saveHouses()

    def putHouse(self,house,saveHouse=False):
        if not house:
            return
        self.houses.append(house)
        if not saveHouse:
            return
        postOffset = 10
        if len(self.houses) >= postOffset:
            self.saveHouses()
    
    def saveHouses(self):
        if not self.houses and len(self.houses) == 0:
            return
        tmpContents = ''
        for house in self.houses:
            if house:
                tmpContents = tmpContents + "\n" + house.toString()
        if tmpContents:
            putContent = 'path=' + self.houseFilename + '&content=' + tmpContents.strip("\n")
            self.redisClient.lpush('put_content',putContent)
        self.houses.clear()
    
    def scanRentHouse(self,saveRent=False,startOffset=1,maxOffset=100):
        hostUrl = 'http://sh.lianjia.com'
        offset = startOffset
        requestErrCount = 0
        while True:
            res = requests.get(hostUrl + '/zufang/d' + str(offset),headers=self.headers)
            if not res or not res.text:
                break
            doc = etree.HTML(res.text)
            houseLinks = doc.xpath('//ul[@id="house-lst"]/li/div[@class="pic-panel"]/a')
            if not houseLinks or len(houseLinks)<=0:
                break
            for houseLink in houseLinks:
                houseHref = houseLink.get('href')
                try:
                    houseRes = requests.get(hostUrl + houseHref,headers=self.headers)
                except:
                    traceback.print_exc()
                    requestErrCount += 1
                    if requestErrCount >= 6:
                        os._exit()
                    continue
                if houseRes and houseRes.text:
                    try:
                        houseDoc = etree.HTML(houseRes.text)
                        houseIdInfo = houseDoc.xpath('//span[@class="houseNum"]')[0].text
                        houseId = houseIdInfo[houseIdInfo.index('：')+1:]
                        price = int(houseDoc.xpath('//div[@class="houseInfo"]/div[@class="price"]/div')[0].text)
                        roomInfo = houseDoc.xpath('//div[@class="houseInfo"]/div[@class="room"]/div')[0].text
                        print(roomInfo)
                        os._exit()
                        
                    except:
                        print("exception href=" + houseHref)
                        traceback.print_exc()
            offset += 1
            if offset >= maxOffset:
                break