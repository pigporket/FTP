#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan
import socket,os,json
import os ,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量

from core import main


if __name__ == '__main__':
    main.ArvgHandler()