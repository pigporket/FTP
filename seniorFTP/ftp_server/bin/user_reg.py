#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan

import configparser
import os ,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
from cfg import config
#修改个信息 磁盘大小
def set_info(name,pwd,size):
    config_info=configparser.ConfigParser()#读数据
    config_info.read(config.AUTH_FILE)#读文件 用户名密码
    #print(config_info.options(name))
    config_info[name]={}
    config_info.set(name,config.PWD,pwd)#密码
    config_info.set(name,config.QUOTATION,size)#磁盘信息
    config_info.write(open(config.AUTH_FILE,'w'))#写入文件
    file_path='%s/%s'%(config.USER_HOME,name)#拼接目录路径
    os.mkdir(file_path)#创建目录
    print('创建完成'.center(60,'='))
    print('用户名:[%s]\n密码:[%s]\n磁盘空间:[%s]'%(name,pwd,size))

if __name__ == '__main__':
    name=input('name:')
    pwd=input('pwd:')
    size=input('size:')
    set_info(name,pwd,size)
