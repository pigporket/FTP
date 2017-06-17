#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan

import os ,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
HOME_PATH = os.path.join(BASE_DIR, "home")
print(BASE_DIR)


#USER_DIR='%s\\data\\'%BASE_DIR#定义用户数据目录文件路径变量
USER_DIR='%s/data'%BASE_DIR#定义用户数据目录文件路径变量
#USER_HOME='%s\\home\\'%BASE_DIR#定义用户家目录文件路径变量
USER_HOME='%s/home'%BASE_DIR#定义用户家目录文件路径变量
#LOG_DIR='%s\\log\\'%BASE_DIR#日志目录
LOG_DIR='%s/log'%BASE_DIR#日志目录
LOG_LEVEL='DEBUG'#日志级别

AUTH_FILE='%s/cfg/userpwd.cfg'%BASE_DIR#用户名密码文件
HOST='0.0.0.0'# IP
PORT=9500#端口
QUOTATION='Quotation'#磁盘空间
PWD='PWD'#密码