#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan
import socketserver,os,json,pickle,configparser

STATUS_CODE={
    240:'格式出错,格式:{"action":"get","filename":"filename","size":100}',
    241:'指令错误',
    242:'用户名或密码为空',
    243:'用户或密码出错',
    244:'用户密码通过校验',
    245:'文件不存在',
    246:'服务器上该文件不存在',
    247:'准备发送文件,请接收',
    248:'md5',
    249:'准备接收文件,请上传',
    250:'磁盘空间不够',
    251:'当前已经为主目录',
    252:'目录正在切换'


}
import os ,sys,hashlib
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
from cfg import config

class MyTCPHandler (socketserver.BaseRequestHandler):#
    def setup(self):
       print('监听中。。。')
    #'''用户名与密码是否为空'''
    def cmd_auth(self,*args,**kwargs):#用户校验
        '''用户名与密码是否为空'''
        data=args[0]#获取 传来的数据
        if data.get('username') is None or data.get('password') is None:#如果用户名或密码为空
            self.send_mge(242)#发送错误码
        name=data.get('username')#用户名
        pwd=data.get('password')#密码
        print(name,pwd)
        user=self.authusername(name,pwd)#用户名与密码的校验 获名用户名
        if user is None:#用户名不存在
            self.send_mge(243)
        else:
            self.user=name#保存用户名
            self.send_mge(244)

    #'''用户名与密码的校验''
    def authusername(self,name,pwd):
        '''用户名与密码的校验'''
        config_info=configparser.ConfigParser()#读数据
        config_info.read(config.AUTH_FILE)#读文件 用户名密码
        if name in config_info.sections():#用户名存
            password=config_info[name]['PWD']
            if password==pwd:#密码正确
                print('通过校验!')
                config_info[name]['USERname']=name#名字的新字段
                return config_info[name]

    #'''客户端上传文件 '''
    def cmd_put(self,*args,**kwargs):
        '''客户端上传文件 '''
        cmd_dict=args[0]#获取字典
        filename =cmd_dict['filename']#文件名
        filesize= cmd_dict['size']#文件大小
        user_home_dir='%s/%s'%(config.USER_HOME,self.user)#拼接 用户home目录路径
        file_path='%s/%s'%(user_home_dir,filename)#拼接文件路径 用户home目录
        attr_list=self.user_info()#调用个人信息
        put_size=attr_list[1]#取得磁盘信息
        print(put_size,type(put_size))
        user_size=float(put_size)*1024000#字节

        if float(filesize)>float(user_size):#空间不足
            self.send_mge(250,data={'剩余空间':user_size})
            print(put_size)
            return
        if os.path.isfile(file_path):#文件是否存
            print(attr_list[1])
            self.send_mge(249,data={'剩余空间':user_size})#发送一个确认
            self.request.recv(1) #客户端确认 防粘包
            f=open(filename+'.new','wb')#建一个新的文件
        else:
            f=open(filename,'wb')

        reversed_size=0#接收到数据大小
        if cmd_dict['md5']:#是否有 md5
            md5_obj = hashlib.md5() #   进行MD5
            while reversed_size< int(filesize):#接收小于文件 大小
                if int(filesize) - reversed_size>1024:#表示接收不止一次
                    size=1024
                else:#最后一次
                    size=int(filesize) - reversed_size
                    #print('最后一个大小',size)
                data= self.request.recv(size)#接收数据
                md5_obj.update(data)
                reversed_size+=len(data)#接收数据大小累加
                f.write(data)#写入文件
            else:
                f.close()
                print('[%s]文件上传完毕'.center(60,'-')%filename)

                md5_val = md5_obj.hexdigest()#得出MD5
                print(md5_val)
                self.send_mge(248,{'md5':md5_val})#发送md5给客户端
        else:
            while reversed_size< int(filesize):#接收小于文件 大小
                if int(filesize) - reversed_size>1024:#表示接收不止一次
                    size=1024
                else:#最后一次
                    size=int(filesize) - reversed_size
                    #print('最后一个大小',size)
                data= self.request.recv(size)#接收数据

                reversed_size+=len(data)#接收数据大小累加
                f.write(data)#写入文件
            else:
                print('[%s]文件上传完毕'%filename.center(60,'-'))
                f.close()
        new_size=float((float(user_size)-float(filesize))/1024000)#扣除空间大小
        self.set_info(str(new_size))#传入新大小


    #用户下载文件
    def cmd_get(self,*args,**kwargs):#用户下载文件
        ''' 用户下载文件'''
        data=args[0]
        print(data)
        if data.get('filename') is None:#判断文件名不为空
            self.send_mge(245)
        print(config.USER_HOME)
        print(self.user)
        user_home_dir='%s/%s'%(config.USER_HOME,self.user)#拼接 用户home目录路径
        #user_home_dir=config.USER_HOME+self.user#拼接 用户home目录路径
        print(user_home_dir)
        #file_path='%s\\%s'%(user_home_dir,data.get('filename'))#拼接文件路径 用户home目录
        file_path='%s/%s'%(user_home_dir,data.get('filename'))#拼接文件路径 用户home目录
        #print("file abs path",file_path)

        if os.path.isfile(file_path):#判断文件是否存在
            file_obj=open(file_path,'rb')#打开文件句柄\
            file_size=os.path.getsize(file_path)#获取文件大小

            self.send_mge(247,data={'file_size':file_size})#发送相关信息
            self.request.recv(1) #客户端确认 防粘包

            if data.get('md5'):
                md5_obj = hashlib.md5()
                for line in file_obj:
                    self.request.send(line)
                    md5_obj.update(line)
                else:
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()
                    self.send_mge(248,{'md5':md5_val})
                    print("发送完毕.")
            else:
                for line in file_obj:
                    self.request.send(line)
                else:
                    file_obj.close()
                    print("发送完毕.")

    #切换目录
    def cmd_cd(self,cmd_dict,*args,**kwargs):
        '''切换目录'''
        self.dir_attr=config.USER_HOME#用户家目录
        self.dir_attr='%s/%s'%(config.USER_HOME,self.user)#拼接 用户home目录路径
        self.home_dir='/'#相对路径
        print(config.USER_HOME)
        print(self.home_dir)
        cmd_attr=cmd_dict['actionname']#获取命令
        if cmd_attr=='..':
            if self.dir_attr==config.USER_HOME:
                self.send_mge(251)
                return
            else:
                self.send_mge(252)#可以切换
                #dir_list=self.dir_attr.split('\\')
                dir_name=self.dir_attr.split('\\')[-1]#获取最后的目录
                #new_dir='\\'.join(dir_list.difference(dir_name))#拼接新的路径
                #print(new_dir)
                clinet_ack=self.request.recv(1024)#为了去粘包
                self.request.send(dir_name.encode())
                return
        else:
            self.send_mge(252)
            new_dir=self.dir_attr+'\\'+cmd_attr
            clinet_ack=self.request.recv(1024)#为了去粘包
            self.request.send(new_dir.encode())
            return


    #修改个信息 磁盘大小
    def set_info(self,new_size):
        config_info=configparser.ConfigParser()#读数据
        config_info.read(config.AUTH_FILE)#读文件 用户名密码
        print(config_info.options(self.user))
        config_info.set(self.user,config.QUOTATION,new_size)
        config_info.write(open(config.AUTH_FILE,'w'))

    #读取个人信息
    def user_info(self):
        config_info=configparser.ConfigParser()#读数据
        config_info.read(config.AUTH_FILE)#读文件 用户名密码
        print(config_info.options(self.user))
        pwds=config_info[self.user][config.PWD]#密码
        Quotation=config_info[self.user][config.QUOTATION]#磁盘配额 剩余
        user_info={}
        user_info['用户名']=self.user
        user_info['密码']=pwds
        user_info['剩余磁盘配额']=Quotation
        return user_info,Quotation

    #查看用户信息
    def cmd_info(self,*args,**kwargs):
        attr=self.user_info()
        print(type(attr))
        print(type(attr[0]))
        self.request.send(str(len(json.dumps(attr[0]))).encode('utf-8'))#
        clinet_ack=self.request.recv(1024)#为了去粘包
        self.request.send(json.dumps(attr[0]).encode('utf-8'))#发送指令


    #目录查看
    def cmd_dir(self,*args,**kwargs):
        user_home_dir='%s/%s'%(config.USER_HOME,self.user)#拼接 用户home目录路径
        #file_path='%s/%s'%(user_home_dir,'tmp')#拼接文件路径 用户home目录下
        data=os.listdir(user_home_dir)#查看目录文件
        datas=json.dumps(data)#转成json格式
        #print(datas)
        self.request.send(str(len(datas.encode('utf-8'))).encode('utf-8'))#发送大小
        clinet_ack=self.request.recv(1024)#为了去粘包
        self.request.send(datas.encode('utf-8'))#发送指令


    ##单个命令
    def cmd_compr(self,cmd_dict,**kwargs):
        attr=cmd_dict['actionname']#赋于变量
        if hasattr(self,'cmd_%s'%attr):#是否存在
            func=getattr(self,'cmd_%s'%attr)#调用
            func(cmd_dict)
            return
        else:
            print('没有相关命令!')
            self.send_mge(241)
            return

    #'''发送信息码给客户端'''
    def send_mge(self,status_code,data=None):
        '''发送信息码给客户端'''
        mge={'status_code':status_code,'status_msg':STATUS_CODE[status_code]}#消息
        if data:#不为空
            mge.update(data)#提示码进行更新
        print(mge)
        self.request.send(json.dumps(mge).encode())#发送给客户端


    #重写handle方法
    def handle(self):#重写handle方法
        while True:
            #try:
            self.data=self.request.recv(1024).strip()#接收数据
            # print(self.client_address[0])#连接的ip
            print('ip:{}'.format(self.client_address[0]))#连接的ip
            print(self.data)
            if not self.data:
                print("客户端断开了!.")
                break
            cmd_dict=json.loads(self.data.decode())#接收 数据
            #print(cmd_dict)
            if cmd_dict.get('action') is not None:#判断数据格式正确
                #print(cmd_dict,'111')
                action=cmd_dict['action']#文件 头
                #print(action)
                if hasattr(self,'cmd_%s'%action):#是否存在
                    func=getattr(self,'cmd_%s'%action)#调用
                    func(cmd_dict)
                else:
                    print('没有相关命令!')
                    self.send_mge(241)
            else:
                print('数据出错!')
                self.send_mge(240)
            #except Exception as e:
             #  print('客户端断开了!',e)
              # break