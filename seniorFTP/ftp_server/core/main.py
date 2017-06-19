#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan

import socketserver,os,json,pickle
import os ,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
from cfg import config


from  core.ftp_server import  MyTCPHandler

import optparse
class ArvgHandler(object):
    def __init__(self):#   可  传入系统参数
        self.paresr=optparse.OptionParser()#启用模块
        #self.paresr.add_option('-s','--host',dest='host',help='服务绑定地址')
        #self.paresr.add_option('-s','--port',dest='host',help='服务端口')
        (options,args)=self.paresr.parse_args()#返回一个字典与列表的元组

        self.verufy_args(options,args)#进行校验
    def verufy_args(self,options,args):
        '''校验与调用'''
        if hasattr(self,args[0]):#反射判断参数
            func=getattr(self,args[0])#生成一个实例
            func()#开始调用
        else:
            self.paresr.print_help()#打印帮助文档
    def start(self):
        print('服务启动中....')
        s=socketserver.ThreadingTCPServer((config.HOST,config.PORT),MyTCPHandler)#实例化一个服务端对象
        s.serve_forever()#运行服务器
        print('服务关闭')