#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan
import os,logging,time
from cfg import config
LOG_LEVEL=config.LOG_LEVEL


def log_log():#登陆日志,传入内容
    logger=logging.getLogger('用户成功登陆日志')#设置日志模块
    logger.setLevel(logging.DEBUG)
    fh=logging.FileHandler(config.USER_LOG,encoding='utf-8')#写入文件
    fh.setLevel(config.LOG_LEVEL)#写入信息的级别
    fh_format=logging.Formatter('%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')#日志格式
    fh.setFormatter(fh_format)#关联格式
    logger.addHandler(fh)#添加日志输出模式
    #logger.warning(info_str)
    return logger

def user_opert():#用户操作日志,传入内容
    logger=logging.getLogger('用户操作日志')#设置日志模块
    logger.setLevel(logging.CRITICAL)
    fh=logging.FileHandler(config.USER_OPERT,encoding='utf-8')#写入文件
    fh.setLevel(config.LOG_LEVEL)#写入信息的级别
    fh_format=logging.Formatter('%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')#日志格式
    fh.setFormatter(fh_format)#关联格式
    logger.addHandler(fh)#添加日志输出模式
    #logger.critical(info_str)
    return logger