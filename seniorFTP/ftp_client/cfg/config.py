#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan

import os ,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
#print(BASE_DIR)

PUT_DIR=BASE_DIR+'\putfile\\'#定义用户上传目录文件路径变量
GET_DIR=BASE_DIR+'\down\\'#定义用户下载目录文件路径变量
HELP='help'
CMD_LIST=['ls','pwd','info','help']