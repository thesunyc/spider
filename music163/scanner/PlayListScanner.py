#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import requests
import json
import redis
import threading
import base64
import jump
import hashlib
import traceback
from Cryptodome.Cipher import AES
from lxml import etree
sys.path.append('E:\workspace\spider')
from base.config.Config import COMMON_HEADERS
from music163.model.Comment import Comment
from music163.model.Song import Song
from music163.scanner.BaseScanner import BaseScanner

class SongScanner(BaseScanner):
    def __init__(self,redisConf,enableCache=False):
        self.redisClient = redis.Redis(redisConf)
        self.headers = COMMON_HEADERS
        self.headers['Cookie'] = 'appver=1.5.0.75771;'
        self.headers['Referer'] = 'http://music.163.com/'
        self.enableCache = enableCache
        self.songBucketCount = 10000
        self.initCommentRequestParam()
    
    def scanSong(self,doc):
        if not doc:
            return
        songLinks = doc.xpath('//a[starts-with(@href,"/song?id=")]')
        if not songLinks or len(songLinks)<=0:
            return
        for songLink in songLinks:
            songId = songLink.get('href')[9:]
            if songId.isdigit():
                if self.existCache(songId):
                    continue
                self.collectSong(songId)
    
    def collectSong(self,songId):
        res = requests.get("http://music.163.com/song?id=" + songId,headers=COMMON_HEADERS)
        if not res or not res.text:
            return
        try:
            doc = etree.HTML(res.text)
            newSong = Song()
            comments = []
            songInfoDiv = doc.xpath('//div[@class="cnt"]')[0]
            newSong.title = songInfoDiv.xpath('.//em[@class="f-ff2"]')[0].text
            artistsLinks = songInfoDiv.xpath('.//p[@class="des s-fc4"][1]//a')
            for artistLink in artistsLinks:
                newSong.artists.append({"id":artistLink.get('href')[11:],"name":artistLink.text})
            albumLink = songInfoDiv.xpath('.//p[@class="des s-fc4"][2]/a')[0]
            newSong.album = {"id":albumLink.get('href')[10:],"name":albumLink.text}
            
            paramData = {
                "params": self.getParams(),
                "encSecKey": self.commentRequestParams['enc_sec_key']
            }
            res = requests.post("http://music.163.com/weapi/v1/resource/comments/R_SO_4_" + songId + "?csrf_token=",headers=self.headers,data=paramData)
            if res and res.text:
                resJson = json.loads(res.text)
                newSong.commentCount = resJson['total']
                #comments
                for comment in resJson['comments']:
                    comments.append(Comment(comment['commentId'],comment['user']['userId'],songId
                        ,comment['content'],comment['likedCount'],comment['time']))
                for comment in resJson['hotComments']:
                    comments.append(Comment(comment['commentId'],comment['user']['userId'],songId
                        ,comment['content'],comment['likedCount'],comment['time']))
            self.saveItems("/music163/song.json",newSong)
            self.saveItems("/music163/comment.json",comments)
        except:
            traceback.print_exc()

    
    def initCommentRequestParam(self):
        self.commentRequestParams = {}
        self.commentRequestParams['first_param'] = "{rid:\"\", offset:\"0\", total:\"true\", limit:\"20\", csrf_token:\"\"}"
        self.commentRequestParams['second_param'] = "010001"
        self.commentRequestParams['third_param'] = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.commentRequestParams['forth_param'] = '0CoJUm6Qyw8W8jud'
        self.commentRequestParams['enc_sec_key'] = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    
    def getParams(self):
        iv = b'0102030405060708'
        first_key = self.commentRequestParams['forth_param']
        second_key = 16 * 'F'
        h_encText = self.AES_encrypt(self.commentRequestParams['first_param'], first_key, iv)
        h_encText = self.AES_encrypt(h_encText, second_key, iv)
        return h_encText
    
    def AES_encrypt(self,text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(bytes(key,encoding="utf8"), AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(bytes(text,encoding="utf8"))
        encrypt_text = base64.b64encode(encrypt_text)
        return bytes.decode(encrypt_text)


