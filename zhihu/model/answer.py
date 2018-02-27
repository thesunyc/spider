#!/usr/bin/env python3
#-*- coding:utf-8 
import json

class Answer:
    def __init__(self,id,question,author,content,createTime,voteupCount,commentCount):
        self.id = str(id)
        self.questionId = str(question.id)
        self.questionName = question.name
        self.authorId = author.id
        self.authorName = author.name
        self.authorGender = author.gender
        self.content = content
        self.createTime = createTime
        self.voteupCount = voteupCount
        self.commentCount = commentCount
    
    def toDic(self):
        dic = self.__dict__.copy()
        return dic
    
    def toString(self):
        return json.dumps(self.toDic(),ensure_ascii=False)