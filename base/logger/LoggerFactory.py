#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import logging

class LoggerFactory:

    @staticmethod
    def getLogger(name,streamLevel=logging.INFO,filename=None,fileLevel=None):
        logger = logging.getLogger(name)
        fomatter = logging.Formatter('%(asctime)s -%(name)s-%(levelname)s-%(module)s:%(message)s')
        #输出到屏幕
        if streamLevel is not None:
            ch = logging.StreamHandler()
            ch.setLevel(streamLevel)
            logger.addHandler(ch)
        #输出到文件
        if filename is not None and fileLevel is not None:
            fh = logging.FileHandler(filename)
            fh.setLevel(fileLevel)
            logger.addHandler(fh)
        return logger
