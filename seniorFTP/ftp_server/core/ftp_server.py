#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan
import socketserver,os,json,pickle,configparser,time
time_format='%Y%m%d%H%M%S'#定义时间格式
times=time.strftime(time_format)#定义时间

STATUS_CODE={
    230:'文件断点继传',
    231:'新文件',
    240:'格式出错,格式:{"action":"get","filename":"filename","size":100}',
    241:'指令错误',
    242:'用户名或密码为空',
    243:'用户或密码出错',
    244:'用户密码通过校验',
    245:'文件不存在或不是文件',
    246:'服务器上该文件不存在',
    247:'准备发送文件,请接收',
    248:'md5',
    249:'准备接收文件,请上传',
    250:'磁盘空间不够',
    251:'当前已经为主目录',
    252:'目录正在切换',
    253:'正在查看路径',
    254:'准备删除文件',
    255:'删除文件完成',
    256:'目录不存在',
    257:'目录已经存在',
    258:'目录创建完成',
    259:'目录删除完成',
    260:'目录不是空的',
}
import os ,sys,hashlib
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
from cfg import config
from core.logs import log_log
from core.logs import user_opert


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
            self.home_dir='%s/%s'%(config.USER_HOME,self.user)#拼接 用户home目录路径 用户根目录
            self.user_home_dir=self.home_dir#当前所在目录
            # self.user_dir=self.user_home_dir.split('/')[-1]#当前所在目录 相对
            self.dir_join()#进行目录拼接
            self.send_mge(244,data={'dir':self.user_dir})#相对 目录

    #目录拼接
    def dir_join(self,*args,**kwargs):
        self.user_dir=self.user_home_dir.split(self.home_dir)[-1]+'/'#当前所在目录 相对
        print(self.user_dir)

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
                info_str='用户[%s],成功登陆'%name
                self.log_log.warning(info_str)#记录日志
                #log_log(info_str)
                return config_info[name]
            else:
                info_str='用户[%s],登陆错误'%name
                #log_log(info_str)
                self.log_log.warning(info_str)#记录日志
                return 0

    #判断文件 是否存在
    def file_name(self,file_path):
        if os.path.isfile(file_path):#文件是否存
            return  True
        else:
            return False

    #判断目录是否存在
    def file_dir(self,file_path):
        if os.path.isdir(file_path):#目录是否存
            return  True
        else:
            return False

    #删除文件
    def cmd_rm(self,*args,**kwargs):
        cmd_dict=args[0]#获取字典
        action=cmd_dict["action"]
        filename =cmd_dict['filename']#文件名
        file_path='%s/%s'%(self.user_home_dir,filename)#拼接文件路径
        if not self.file_name(file_path):
            self.send_mge(245)#文件不存在
            return
        else:
            user_size=self.disk_size()#获取磁盘信息
            self.send_mge(254,data={'剩余空间':user_size})#准备删除文件
            file_size=os.path.getsize(file_path)#获取文件大小
            pass
        self.request.recv(1) #客户端确认 防粘包
        os.remove(file_path)
        new_size=float((float(user_size)+float(file_size))/1024000)#空间大小增加
        self.set_info(str(new_size))#传入新大小
        self.send_mge(255,data={'剩余空间':new_size})#删除文件完成
        info_str=self.log_str('删除文件')#生成日志信息
        self.user_opert.critical(info_str)#记录日志
        return

    #创建目录
    def cmd_mkdir(self,*args,**kwargs):
        cmd_dict=args[0]#获取字典
        action=cmd_dict["action"]
        filename =cmd_dict['filename']#目录名
        file_path='%s/%s'%(self.user_home_dir,filename)#拼接目录路径
        if self.file_dir(file_path):
            self.send_mge(257)#目录已经 存在
            return
        else:
            self.send_mge(256,data={'目录':'创建中...'})#目录创建中
            self.request.recv(1) #客户端确认 防粘包
            os.mkdir(file_path)#创建目录
            self.send_mge(258)#目录完成
            info_str=self.log_str('创建目录')#生成日志信息
            self.user_opert.critical(info_str)#记录日志
            return

    #删除目录
    def cmd_rmdir(self,*args,**kwargs):
        cmd_dict=args[0]#获取字典
        action=cmd_dict["action"]
        filename =cmd_dict['filename']#目录名
        file_path='%s/%s'%(self.user_home_dir,filename)#拼接目录路径
        if not self.file_dir(file_path):
            self.send_mge(256)#目录不存在
            return
        elif os.listdir(file_path):
            self.send_mge(260,data={'目录':'无法删除'})#目录不是空的
            return
        else:
            self.send_mge(257,data={'目录':'删除中...'})#目录创建中
            self.request.recv(1) #客户端确认 防粘包
            os.rmdir(file_path)#删除目录
            self.send_mge(259)#目录删除完成
            info_str=self.log_str('删除目录')#生成日志信息
            self.user_opert.critical(info_str)#记录日志
            return

    #磁盘空间大小
    def disk_size(self):
        attr_list=self.user_info()#调用个人信息
        put_size=attr_list[1]#取得磁盘信息
        user_size=float(put_size)*1024000#字节
        return user_size

    #'''客户端上传文件 '''
    def cmd_put(self,*args,**kwargs):
        '''客户端上传文件 '''
        cmd_dict=args[0]#获取字典
        filename =cmd_dict['filename']#文件名
        file_size= cmd_dict['size']#文件大小
        #user_home_dir='%s/%s'%(config.USER_HOME,self.user)#拼接 用户home目录路径
        file_path='%s/%s'%(self.user_home_dir,filename)#拼接文件路径
        user_size=self.disk_size()#取得磁盘信息
        if float(file_size)>float(user_size):#空间不足
            self.send_mge(250,data={'剩余空间':user_size})
            return
        self.send_mge(249,data={'剩余空间':user_size})#发送一个确认
        self.request.recv(1) #客户端确认 防粘包
        if self.file_name(file_path):#判断文件名是否存在,
            s_file_size=os.path.getsize(file_path)##获取服务器上的文件大小
            if file_size>s_file_size:#如果服务器上的文件小于要上传的文件进
                tmp_file_size=os.stat(file_path).st_size#计算临时文件大小
                reversed_size=tmp_file_size#接收到数据大小
                self.send_mge(230,data={'文件大小':reversed_size})#发送临时文件大小
                pass
            else:# file_size==s_file_size:#如果大小一样
                file_path=file_path+'_'+times#命名新的文件 名
                reversed_size=0#接收到数据大小
                self.send_mge(231)#发送 不是断点文件
                pass
        else:
            reversed_size=0#接收到数据大小
            self.send_mge(231)#发送 不是断点文件
            pass

        f=open(file_path,'ab')
        self.request.recv(1) #客户端确认 防粘包
        if cmd_dict['md5']:#是否有 md5
            md5_obj = hashlib.md5() #   进行MD5
            while reversed_size< int(file_size):#接收小于文件 大小
                if int(file_size) - reversed_size>1024:#表示接收不止一次
                    size=1024
                else:#最后一次
                    size=int(file_size) - reversed_size
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
            while reversed_size< int(file_size):#接收小于文件 大小
                if int(file_size) - reversed_size>1024:#表示接收不止一次
                    size=1024
                else:#最后一次
                    size=int(file_size) - reversed_size
                    #print('最后一个大小',size)
                data= self.request.recv(size)#接收数据
                reversed_size+=len(data)#接收数据大小累加
                f.write(data)#写入文件
            else:
                print('[%s]文件上传完毕'%filename.center(60,'-'))
                f.close()
        new_size=float((float(user_size)-float(file_size))/1024000)#扣除空间大小
        self.set_info(str(new_size))#传入新大小
        info_str=self.log_str('文件上传')#生成日志信息
        self.user_opert.critical(info_str)#记录日志
        return

    #用户下载文件
    def cmd_get(self,*args,**kwargs):#用户下载文件
        ''' 用户下载文件'''
        data=args[0]
        print(data)
        if data.get('filename') is None:#判断文件名不为空
            self.send_mge(245)
            return

        self.request.recv(1) #客户端确认 防粘包
        file_path='%s/%s'%(self.user_home_dir,data.get('filename'))#拼接文件路径 用户文件路径
        if os.path.isfile(file_path):#判断文件是否存在
            file_obj=open(file_path,'rb')#打开文件句柄\
            file_size=os.path.getsize(file_path)#获取文件大小
            if data['name_down']:
                send_size=data['size']#已经发送数据大小
                #self.send_mge(230,data={'文件大小':file_size})#断点续传
            else:
                send_size=0
                #self.send_mge(231)#非断点续传
            #self.request.recv(1) #客户端确认 防粘包
            file_obj.seek(send_size)#移动到
            self.send_mge(247,data={'file_size':file_size})#发送相关信息
            attr=self.request.recv(1024) #客户端确认 防粘包
            if attr.decode()=='2':return #如果返回是
            if data.get('md5'):
                md5_obj = hashlib.md5()
                while send_size<file_size:
                    line=file_obj.read(1024)
                #for line in file_obj:
                    self.request.send(line)
                    md5_obj.update(line)
                else:
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()
                    self.send_mge(248,{'md5':md5_val})
                    print("发送完毕.")
            else:
                while send_size<file_size:
                    line=file_obj.read(1024)
                #for line in file_obj:
                    self.request.send(line)
                else:
                    file_obj.close()
                    print("发送完毕.")
            self.request.recv(1) #客户端确认 防粘包
            info_str=self.log_str('下载文件')#生成日志信息
            #user_opert(info_str)#记录日志
            self.user_opert.critical(info_str)#记录日志
            return

    #切换目录
    def cmd_cd(self,cmd_dict,*args,**kwargs):
        '''切换目录'''
        cmd_attr=cmd_dict['actionname']#获取命令
        if cmd_attr=='..' or cmd_attr=='../..':
            if (self.home_dir)==self.user_home_dir:
                self.send_mge(251)
                return
            elif cmd_attr=='../..':
                self.send_mge(252)#可以切换到上级目录
                self.user_home_dir=self.home_dir#绝对目录 = home
                self.user_dir='/'
                clinet_ack=self.request.recv(1024)#为了去粘包
                self.request.send(self.user_dir.encode())#返回相对目录
                return
            else:
                self.send_mge(252)#可以切换到上级目录
                print(self.user_home_dir)#绝对目录
                print(os.path.dirname(self.user_home_dir))#父级目录
                self.user_home_dir=os.path.dirname(self.user_home_dir)#父级目录
                self.dir_join()#目录拼接切换
                clinet_ack=self.request.recv(1024)#为了去粘包
                self.request.send(self.user_dir.encode())#返回相对目录
                return

        elif os.path.isdir(self.user_home_dir+'/'+cmd_attr):#如果目录存在
            self.send_mge(252)
            self.user_home_dir=self.user_home_dir+'/'+cmd_attr#目录拼接
            self.dir_join()#相对目录拼接切换
            clinet_ack=self.request.recv(1024)#为了去粘包
            print(clinet_ack.decode())
            self.request.send(self.user_dir.encode())
            return
        else:
            self.send_mge(256)#目录不存在
            return

    #查看目录路径 CD
    def cmd_pwd(self,cmd_dict):
        self.request.send(str(len(self.user_dir.encode('utf-8'))).encode('utf-8'))#发送大小
        clinet_ack=self.request.recv(1024)#为了去粘包
        self.request.send(self.user_dir.encode())#发送相对路径
        info_str=self.log_str('查看目录路径')#生成日志信息
        #logger.warning
        self.user_opert.critical(info_str)#记录日志
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
        info_dict=attr[0]
        self.request.send(str(len(json.dumps(info_dict))).encode('utf-8'))#
        clinet_ack=self.request.recv(1024)#为了去粘包
        self.request.send(json.dumps(info_dict).encode('utf-8'))#发送指令
        info_str=self.log_str('查看用户信息')#生成日志信息
        self.user_opert.critical(info_str)#记录日志
        return

    #日志信息生成
    def log_str(self,msg,**kwargs):
        info_str='用户[%s]进行了[%s]操作'%(self.user,msg)
        return info_str


    #目录查看
    def cmd_ls(self,*args,**kwargs):
        data=os.listdir(self.user_home_dir)#查看目录文件
        print(data)
        datas=json.dumps(data)#转成json格式
        self.request.send(str(len(datas.encode('utf-8'))).encode('utf-8'))#发送大小
        clinet_ack=self.request.recv(1024)#为了去粘包
        self.request.send(datas.encode('utf-8'))#发送指令
        info_str=self.log_str('目录查看')#生成日志信息
        self.user_opert.critical(info_str)#记录日志
        return
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
            print('ip:{}'.format(self.client_address[0]))#连接的ip
            print(self.data)
            self.log_log=log_log()#登陆日志
            self.user_opert=user_opert()#操作日志
            if not self.data:
                print("[%s]客户端断开了!."%self.user)
                info_str='用户[%s],退出'%self.user

                break
            cmd_dict=json.loads(self.data.decode())#接收 数据
            if cmd_dict.get('action') is not None:#判断数据格式正确
                action=cmd_dict['action']#文件 头
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