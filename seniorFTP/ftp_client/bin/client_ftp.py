#！usr/bin/env python
#-*-coding:utf-8-*-
# Author calmyan
import socket,os,json,getpass,hashlib
import os ,sys,optparse

STATUS_CODE={
    240:'格式出错,格式:{"action":"get","filename":"filename","size":100}',
    241:'指令错误',
    242:'用户密码出错',
    243:'用户或密码出错',
    244:'用户密码通过校验',
}
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取相对路径转为绝对路径赋于变量
sys.path.append(BASE_DIR)#增加环境变量
from cfg import config
class FTPClient(object):
    def __init__(self):
        paresr=optparse.OptionParser()
        paresr.add_option('-s','--server',dest='server',help='服务器地址')
        paresr.add_option('-P','--port',type="int",dest='port',help='服务器端口')
        paresr.add_option('-u','--username',dest='username',help='用户名')
        paresr.add_option('-p','--password',dest='password',help='密码')
        (self.options,self.args)=paresr.parse_args()#返回一个字典与列表的元组
        self.verify_args(self.options,self.args)#判断参数
        self.ser_connect()#连接服务端
        self.cmd_list=config.CMD_LIST

    #实例化一个连接端
    def ser_connect(self):
        self.c=socket.socket()#实例化一个连接端
        self.c.connect((self.options.server,self.options.port))#进行连接

    #判断用户与密码是否成对出现
    def verify_args(self,options,args):
        if (options.username is None and options.password is None) or (options.username is not None and options.password is not None):#判断用户与密码是否成对出现
            pass##判断用户与密码单个出现
        else:
            exit('出错:请输入用户与密码!')#退出
        if options.server and options.port:#端口判断
            if options.port>0 and options.port<65535:
                return True
            else:
                print('端口号:[%s]错误,端口范围:0-65535'%options.port)

    #登陆方法
    def landing(self):#登陆方法
        '''用户验证'''
        if self.options.username is not None:#判断用户名已经输入
            #print(self.options.username,self.options.password)
            return self.get_user_pwd(self.options.username,self.options.password)#返回结果
        else:
            print('用户登陆'.center(60,'='))
            ret_count=0#验证次数
            while ret_count<5:
                username=input('用户名:').strip()
                password=getpass.getpass('密码:').strip()
                if self.get_user_pwd(username,password):
                    return self.get_user_pwd(username,password)#调用远程验证用户 返回结果
                else:
                    ret_count+=1#次数加一
                    print('认证出错次数[%s]'%ret_count)

    #'''用户名与密码检验'''
    def get_user_pwd(self,username,password):
        '''用户名与密码检验'''
        #发送 头文件
        data={
            'action':'auth',
            'username':username,
            'password':password
        }
        self.c.send(json.dumps(data).encode())#发送到服务器
        response = self.get_response()#得到服务端的回复
        if response.get('status_code') == 244:
            print(STATUS_CODE[244])
            self.user = username#存下用户名
            return True
        else:
            print(response.get("status_msg") )

    #服务器回复
    def get_response(self):#服务器回复
        '''服务器回复信息'''
        data=self.c.recv(1024)#接收回复
        data = json.loads(data.decode())
        return data

    #指令帮助
    def help(self):#指令帮助
        attr='''
        help            指令帮助
        ----------------------------------
        info            个人信息
        ----------------------------------
        ls              查看当前目录(linux)
        ----------------------------------
        dir             查看当前目录(windows)
        ----------------------------------
        pwd             查看当前路径(linux)
        ----------------------------------
        cd              查看当前路径(windows)
        ----------------------------------
        cd 目录         切换目录(linux)
        ----------------------------------
        get filename    下载文件
        ----------------------------------
        put filename    上传文件
        ----------------------------------
        --md5           使用md5  在get/put 后
        ----------------------------------
        mkdir name      创建目录(linux)
        ----------------------------------
        md name         创建目录(windows)
        ----------------------------------
        mv filename     移动文件
        ----------------------------------
        rm filename     删除文件
        ----------------------------------
        copy filename   复制文件
        ----------------------------------
        exit            退出
        ----------------------------------
        '''.format()
        print(attr)

    ##交互
    def inter(self):#交互
        if  self.landing():#通过用户密码认证
            print('指令界面'.center(60,'='))
            self.help()
            while True:
                cmd = input('[%s]-->指令>>>:'%self.user).strip()
                if len(cmd)==0:continue#输入空跳过
                if cmd=='exit':exit()#退出指令
                cmd_str=cmd.split()#用空格分割 取命令到列表
                #print(cmd_str)
                #print(len(cmd_str))
                if len(cmd_str)==1 and cmd_str[0] in self.cmd_list:#如果是单个命令 并且在命令列表中
                #if len(cmd_str)==1:#如果是单个命令 并且在命令列表中
                    if cmd_str[0]==config.HELP:
                        self.help()
                        continue
                    func=getattr(self,'cmd_compr')#调用此方法
                    ret=func(cmd_str)
                    if ret:
                        continue
                    else:
                        pass
                elif len(cmd_str)>1:
                    if hasattr(self,'cmd_%s'%cmd_str[0]):#判断类中是否有此方法
                        func=getattr(self,'cmd_%s'%cmd_str[0])#调用此方法
                        func(cmd_str)#执行
                        continue
                else:
                    print('指令出错!')
                    self.help()#

    #'''是否要md5'''
    def cmd_md5_(self,cmd_list):
        '''是否要md5'''
        if '--md5' in cmd_list:
            return True

    #进度条
    def show_pr(self,total):#进度条
        received_size = 0 #发送的大小
        current_percent = 0 #
        while received_size < total:
             if int((received_size / total) * 100 )   > current_percent :
                  print("#",end="",flush=True)#进度显示
                  current_percent = int((received_size / total) * 100 )
             new_size = yield #断点跳转 传入的大小
             received_size += new_size
    #上传方法

    #查看命令
    # def cmd_dir(self,cmd_str,**kwargs):
    #     mag_dict={
    #                 "action":"dir",
    #                 'actionname':cmd_str[0]
    #             }
    #     self.c.send(json.dumps(mag_dict).encode('utf-8'))#发送数据

    #单个命令
    def cmd_compr(self,cmd_str,**kwargs):
        mag_dict={
                    "action":"compr",
                    'actionname':cmd_str[0]
                }
        self.c.send(json.dumps(mag_dict).encode('utf-8'))#发送数据
        data=self.c.recv(1024)#接收数据 数据
        cmd_res_attr=json.loads(data)
        #print(type(cmd_res_attr))
        if type(cmd_res_attr) is not int:#如果不int 类型
            if cmd_res_attr["status_code"] ==241:#命令不对
                #print(data)
                print(cmd_res_attr['status_msg'])
                return
            if cmd_res_attr["status_code"] ==240:#命令不对
                print(cmd_res_attr['status_msg'])
                return

        print('数据大小:',cmd_res_attr)
        size_l=0#收数据当前大小
        self.c.send('准备好接收了，可以发了'.encode('utf-8'))
        receive_data= ''.encode()
        while size_l< cmd_res_attr:
            data=self.c.recv(1024)#开始接收数据
            size_l+=len(data)#加上
            receive_data += data
        else:
            receive_data=receive_data.decode()
            receive_data=eval(receive_data)#转为列表 或字典
            if type(receive_data) is dict:#如果是字典
                for i in receive_data:
                    print(i,receive_data[i])
            if type(receive_data) is list:#如果是列表
                for i in receive_data:
                    print(i)

            return 1

    #切换目录
    def cmd_cd(self,cmd_list,**kwargs):
        '''切换目录'''
        mag_dict={
                    "action":"cd",
                    'actionname':cmd_list[1]
                }
        self.c.send(json.dumps(mag_dict).encode('utf-8'))#发送数据
        msg_l=self.c.recv(1024)#接收数据 消息
        data=json.loads(msg_l.decode())
        if data["status_code"] ==251:#目录不可切换
            print(data)
            print(data['status_msg'])
            return
        elif data["status_code"] ==252:#目录可以换
            self.c.send(b'1')#发送到服务器,表示可以了
            data=self.c.recv(1024)
            print(data.decode())
            return


    #上传方法
    def cmd_put(self,cmd_list,**kwargs):#上传方法
        if len(cmd_list) > 1:
            filename=cmd_list[1]#取文件名
            filename_dir=config.PUT_DIR+filename#拼接文件名路径
            #print(filename)
            #print(filename_dir)
            if os.path.isfile(filename_dir):#是否是一个文件
                filesize=os.stat(filename_dir).st_size#获取文件大小
                #执行行为 名字,大小,是否
                mag_dict={
                    "action":"put",
                    'filename':filename,
                    'size':filesize,
                    'overridden':True,
                    'md5':False
                }
                if self.cmd_md5_(cmd_list):#判断是否进行MD5
                    mag_dict['md5'] = True
                self.c.send(json.dumps(mag_dict).encode('utf-8'))#发送文件信息
                server_response=self.c.recv(1024)#服务器返回 确认
                data=json.loads(server_response.decode())
                if data["status_code"] ==250:#磁盘空间
                    print(data['status_msg'])
                    print(mag_dict['size'])
                    return
                if data["status_code"] ==249:#如文件存在
                    print(data['status_msg'])
                    print('剩余空间',data['剩余空间'])
                    self.c.send(b'1')#发送到服务器,表示可以上传文件了
                    f=open(filename_dir,'rb')#打开文件
                    print(mag_dict['md5'])
                    if mag_dict['md5']==True:
                        md5_obj = hashlib.md5()#定义MD5
                        progress = self.show_pr(mag_dict['size']) #进度条 传入文件大小
                        progress.__next__()
                        for line in f:
                            self.c.send(line)
                            try:
                                progress.send(len(line))#传入当前数据大小
                            except StopIteration as e:
                                print("100%")
                            md5_obj.update(line)#计算MD5
                        else:
                            print(filename,'发送完成!')
                            f.close()
                            md5_val = md5_obj.hexdigest()
                            md5_from_server = self.get_response()#服务端的MD5
                            if md5_from_server['status_code'] == 248:
                                if md5_from_server['md5'] == md5_val:
                                    print("%s 文件一致性校验成功!" % filename)
                                    return
                    else:
                        progress = self.show_pr(mag_dict['size']) #进度条 传入文件大小
                        progress.__next__()
                        for line in f:
                            self.c.send(line)
                            try:
                                progress.send(len(line))#传入当前数据大小
                            except StopIteration as e:
                                print("100%")
                            #print(line)
                        else:
                            print(filename,'发送完成!')
                            f.close()
                            return
            else:
                print(filename,'文件不存在!')

    #下载方法
    def cmd_get(self,cmd_list,**kwargs):#下载方法
        #cmd_split= args[0].split()#指令解析
        # if len(cmd_list) == 1:
        #     print("没有输入文件名.")
        #     return
        mag_dict={
                    "action":"get",
                    'filename':cmd_list[1],
                }
        if self.cmd_md5_(cmd_list):#判断是否进行MD5
            mag_dict['md5'] = True
        self.c.send(json.dumps(mag_dict).encode())#发送
        response = self.get_response()#服务器返回文件 的信息
        if response["status_code"] ==247:#如文件存在
            self.c.send(b'1')#发送到服务器,表示可以接收文件了
            down_filename = cmd_list[1].split('/')[-1]#文件名
            received_size = 0#当前接收的数据大小
            file_path='%s/%s'%(config.GET_DIR,down_filename)#拼接文件路径 用户down目录
            file_obj = open(file_path,"wb")#打开文件
            if self.cmd_md5_(cmd_list):
                md5_obj = hashlib.md5()
                progress = self.show_pr(response['file_size']) #进度条 传入文件大小
                progress.__next__()
                while received_size< response['file_size']:
                    if response['file_size'] - received_size>1024:#表示接收不止一次
                        size=1024
                    else:#最后一次
                        size=response['file_size'] - received_size
                        #print('最后一个大小',size)
                    data= self.c.recv(size)#接收数据

                    try:
                        progress.send(len(data))#传入当前数据大小
                    except StopIteration as e:
                        print("100%")
                    received_size+=len(data)#接收数据大小累加
                    file_obj.write(data)#写入文件
                    md5_obj.update(data)#进行MD5验证
                else:
                    print("下载完成".center(60,'-'))
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()#获取MD5
                    #print(md5_val)
                    md5_from_server = self.get_response()#服务端的MD5
                    #print(md5_from_server['md5'])
                    if md5_from_server['status_code'] == 248:
                        if md5_from_server['md5'] == md5_val:
                            print("%s 文件一致性校验成功!" % down_filename)
            else:
                progress = self.show_pr(response['file_size']) #进度条 传入文件大小
                progress.__next__()
                while received_size< response['file_size']:
                    if response['file_size'] - received_size>1024:#表示接收不止一次
                        size=1024
                    else:#最后一次
                        size=response['file_size'] - received_size
                        print('最后一个大小',size)
                    data= self.c.recv(size)#接收数据

                    try:
                      progress.send(len(data))#传入当前数据大小
                    except StopIteration as e:
                      print("100%")
                    received_size+=len(data)#接收数据大小累加
                    file_obj.write(data)#写入文件

                else:
                    print("下载完成".center(60,'-'))
                    file_obj.close()


if __name__=='__main__':

    c=FTPClient()
    c.inter()