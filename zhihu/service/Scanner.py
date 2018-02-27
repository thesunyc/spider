#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
sys.path.append('E:\workspace\spider')
import requests
import json
import urllib
import uuid
from lxml import etree
from zhihu.model.question import Question
from zhihu.model.topic import Topic
from zhihu.model.author import Author
from zhihu.model.answer import Answer
from dao.hdfsClient import HDFSClient
import time
import redis
import threading

class Scanner:
    def __init__(self,headers={},authorization=None,questionFilename='/zhihu/question.json',answerFilename='/zhihu/answer.json',saveUrl='http://139.196.123.29:8081',redisHost='139.196.123.29',redisPassword='redis1qaz2wsx'):
        self.headers = headers
        self.headers['authorization'] = authorization
        self.questionFilename = questionFilename
        self.answerFilename = answerFilename
        self.saveUrl = saveUrl
        self.answerThreadList = []
        self.redisHost = redisHost
        self.redisPassword = redisPassword
        self.redisClient = redis.Redis(host=self.redisHost,password=self.redisPassword)

    def scanQuestion(self,query,questionSize=999,saveQuestion=False,scanAnswer=False,saveAnswer=False):
        url = 'https://www.zhihu.com/api/v4/search_v3?t=general&q=' + urllib.parse.quote(query) + '&correction=1'
        questions = {}
        offset = 1
        limit = questionSize * 3 if questionSize < 10 else 30
        while True:
            res = requests.get(url + '&offset=' + str(offset) + '&limit=' + str(limit),headers=self.headers)
            if not res or not res.text:
                return questions
            resJson = json.loads(res.text)
            if not resJson or not 'data' in resJson:
                return questions
            for dataObj in resJson['data']:
                if 'object' in dataObj:
                    if 'question' in dataObj['object']:
                        questionObj = dataObj['object']['question']
                        questionName = questionObj['name'].replace('<em>','').replace('</em>','')
                        if(questionName not in questions):
                            questions[questionName] = self.buildQuestion(Question(questionObj['id'],questionName,questionObj['type'],questionObj['url']),scanAnswer=scanAnswer,saveAnswer=saveAnswer)
                            if(len(questions) >= questionSize):
                                return questions
            if resJson['paging']['is_end']:
                return questions
            offset += limit
            time.sleep(1)

    def scanTopicTopQuestion(self,topicId,saveQuestion=False,scanAnswer=False,saveAnswer=False):
        questions = {}
        currentPageIndex = 1
        topAnswerCount = 0
        pageSize = 0
        while True:
            url = "https://www.zhihu.com/topic/" + topicId + "/top-answers?page=" + str(currentPageIndex)
            res = requests.get(url,headers=self.headers)
            if not res or not res.text:
                break
            doc = etree.HTML(res.text)
            if topAnswerCount == 0:
                topAnswerCount = int(doc.xpath('//meta[@itemprop="topAnswerCount"]')[0].get('content'))
                print('topAnswerCount:' + str(topAnswerCount))
                pageSize = int(topAnswerCount/20) + 1
                print('pageSize:' + str(pageSize))
            questionLinks = doc.xpath('//div[@class="zm-topic-list-container"]//a[@class="question_link"]')
            for questionLink in questionLinks:
                questionId = questionLink.get('href').strip('/').split('/')[1]
                if questionId not in questions:
                    questions[questionId] = self.buildQuestion(Question(questionId,questionLink.text.strip('\n'),'question',questionLink.get('href')),scanAnswer=scanAnswer,saveAnswer=saveAnswer)
            if currentPageIndex >= pageSize:
                break
            else:
                currentPageIndex = currentPageIndex + 1
                time.sleep(1)
        if saveQuestion:
            self.putQuestions(questions)
        for t in self.answerThreadList:
            if t.is_alive():
                t.join()
        return questions

    def buildQuestion(self,question,scanAnswer=False,saveAnswer=False):
        questionRes = requests.get('https://www.zhihu.com/question/' + question.id,headers=self.headers)
        if not questionRes or not questionRes.text:
            print('question not found:question.id=' + question.id)
            return None
        doc = etree.HTML(questionRes.text)
        topicDivs = doc.xpath('//div[@class="Tag QuestionTopic"]')
        for topicDiv in topicDivs:
            topicUrl = topicDiv.xpath('.//a/@href')[0]
            topicText = topicDiv.xpath('.//div/div')[0].text
            question.topics.append(Topic(topicUrl.split('/')[-1],topicText,topicUrl))
        commentButton = doc.xpath('//div[@class="QuestionHeader-Comment"]/button')
        if len(commentButton) > 0:
            diter = doc.xpath('//div[@class="QuestionHeader-Comment"]/button')[0].itertext()
            for dtext in diter:
                if '条评论' in dtext:
                    question.commentCount = int(dtext.split(' ')[0].replace(',',''))
        followStatusDiv = doc.xpath('//div[@class="NumberBoard QuestionFollowStatus-counts"]')
        if len(followStatusDiv) > 0:
            question.followCount = followStatusDiv[0].xpath('.//div[@class="NumberBoard-value"]')[0].text
            question.visitCount = followStatusDiv[0].xpath('.//div[@class="NumberBoard-value"]')[1].text
        #answer
        if scanAnswer:
            t = threading.Thread(target=self.scanAnswer,args=(question.id,saveAnswer))
            t.start()
            self.answerThreadList.append(t)
        return question

    def scanAnswer(self,questionId,saveAnswer=False):
        url = "https://www.zhihu.com/api/v4/questions/" + questionId + "/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics&sort_by=default"
        answerlist = []
        offset = 0
        limit = 20
        while True:
            res = requests.get(url + '&offset=' + str(offset) + '&limit=' + str(limit),headers=self.headers)
            if not res or not res.text:
                break
            resJson = json.loads(res.text)
            if not resJson or not 'data' in resJson:
                break
            for dataObj in resJson['data']:
                if 'question' in dataObj and 'author' in dataObj and 'content' in dataObj and dataObj['content']:
                    questionData = dataObj['question']
                    question = Question(questionData['id'],questionData['title'],questionData['type'],questionData['url'])
                    authorData = dataObj['author']
                    author = Author(authorData['id'],authorData['name'],authorData['headline'],authorData['gender'],authorData['is_org'])
                    answerContent = str(etree.tostring(etree.HTML(dataObj['content']),encoding='UTF-8',method="html"),encoding='UTF-8').replace('\n','')
                    answerlist.append(Answer(dataObj['id'],question,author,answerContent,dataObj['created_time'],dataObj['voteup_count'],dataObj['comment_count']))    
            if resJson['paging']['is_end']:
                break
            offset += limit
            time.sleep(1)
        if saveAnswer:
            self.putAnswers(answerlist)
        return answerlist
    
    def saveQuestions(self,questions):
        if not questions or len(questions) == 0:
            return
        postOffset = 10
        tmpContents = ''
        index = 0
        dataSize = len(questions)
        for question in questions.values():
            if tmpContents:
                tmpContents = tmpContents + "\n" + question.toString()
            if((index % postOffset == 0 or index == dataSize-1) and tmpContents):
                postContent = urllib.parse.urlencode({'path':self.questionFilename,'content':tmpContents.strip("\n")})
                postHeaders = {"Content-Type":"application/x-www-form-urlencoded"}
                res = requests.post(url=self.saveUrl,data=postContent,headers=postHeaders)
                tmpContents = ''
            index = index + 1
        
    def saveAnswers(self,answerList):
        if not answerList or len(answerList) == 0:
            return
        postOffset = 10
        tmpContents = ''
        index = 0
        dataSize = len(answerList)
        for answer in answerList:
            if answer:
                answer.content = self.encodeContent(answer.content)
                tmpContents = tmpContents + "\n" + answer.toString()
            if((index % postOffset == 0 or index == dataSize-1) and tmpContents):
                postContent = urllib.parse.urlencode({'path':self.answerFilename,'content':tmpContents.strip("\n")})
                postHeaders = {"Content-Type":"application/x-www-form-urlencoded"}
                res = requests.post(url=self.saveUrl,data=postContent,headers=postHeaders)
                tmpContents = ''
            index = index + 1
    
    def putQuestions(self,questions):
        if not questions or len(questions) == 0:
            return
        postOffset = 10
        tmpContents = ''
        index = 0
        dataSize = len(questions)
        for question in questions.values():
            if question:
                tmpContents = tmpContents + "\n" + question.toString()
            if((index % postOffset == 0 or index == dataSize-1) and tmpContents):
                putContent = 'path=' + self.questionFilename + '&content=' + tmpContents.strip("\n")
                self.redisClient.lpush('zhihu_content',putContent)
                tmpContents = ''
            index = index + 1
    
    def putAnswers(self,answerList):
        if not answerList or len(answerList) == 0:
            return
        postOffset = 10
        tmpContents = ''
        index = 0
        dataSize = len(answerList)
        for answer in answerList:
            if answer:
                tmpContents = tmpContents + "\n" + answer.toString()
            if((index % postOffset == 0 or index == dataSize-1) and tmpContents):
                putContent = 'path=' + self.answerFilename + '&content=' + tmpContents.strip("\n")
                self.redisClient.lpush('zhihu_content',putContent)
                tmpContents = ''
            index = index + 1
    
    def encodeContent(self,content):
        return content.replace(';','__FENHAO__').replace(',','__DOUHAO__').replace('&','__YUHAO__')