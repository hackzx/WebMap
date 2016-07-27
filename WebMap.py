# encoding: UTF-8

import argparse
import IPy
import socket
import Queue
import threading
import requests
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

TimeOut=5

#User-Agent
header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36','Connection':'close'}

# 参数
parser=argparse.ArgumentParser(prog='WebMap', description='''\
NIXI WebMap v0.1
''', epilog='方便快捷！')
parser.add_argument('ip', help='10.0.0.1-10.0.0.255 or 10.0.0.0/24 or domain.com')
parser.add_argument('-s', '--scan', help='执行简单敏感文件扫描', action='store_false')
parser.add_argument('-t', '--thread', metavar='num', help='自定义线程，默认100', default=100)
parser.add_argument('-p', '--port', help='自定义端口，默认全部扫描', metavar='port', default='80,8080,7001,8000,8008,8088,8090,9000,9001,9043,9080,9090')
args=parser.parse_args()

# 把「10.0.0.1-10.0.0.255」和「10.0.0.0/24」两种格式的IP转为list的函数都放在这里了。
def ip2num(ip):
    ip=[int(x) for x in ip.split('.')]
    return ip[0] <<24 | ip[1]<<16 | ip[2]<<8 |ip[3]
def num2ip(num):
    return '%s.%s.%s.%s' %( (num & 0xff000000) >>24,
                            (num & 0x00ff0000) >>16,
                            (num & 0x0000ff00) >>8,
                            num & 0x000000ff )
def get_ip(ip):
    start,end = [ip2num(x) for x in ip.split('-') ]
    return [ num2ip(num) for num in range(start,end+1) if num & 0xff ]
def domain2ip(domain):
    try:
        result = socket.getaddrinfo(domain, None)
        return result[0][4][0]
    except:
        return 0

# 把iplist放入队列
ipQueue=Queue.Queue()
def iplist2queue():
    for x in iplist:
        x=str(x)
        ipQueue.put(x)

# 敏感文件扫描
def dirScan(ip):
    ishttp = ip.find('http://')
    if ishttp<0:
        ip = 'http://' + ip
    for port in ports:
        with open('./dict','r') as f:
            for line in f:
                url = ip + ':' + port + '/' + line.strip('\n').strip('\r')
                # r = requests.get('http://github.com', allow_redirects=False) 禁用重定向
                try:
                    r=requests.Session().head(url, headers=header, timeout=TimeOut)
                except Exception, e:
                    pass
                else:
                    pass
                finally:
                    try:
                        if r.status_code == 200:
                            print '\033[32m' + '%s -------- %d OK' %(url, r.status_code)  + '\033[0m'
                        elif r.status_code == 403:
                            print '\033[33m' + '%s -------- %d Forbidden' %(url, r.status_code)  + '\033[0m'
                        elif r.status_code == 500:
                            print '\033[1;36m' + '%s -------- %d Forbidden' %(url, r.status_code)  + '\033[0m'
                        else:
                            print '\033[91m' + '%s -------- %d' %(url, r.status_code)  + '\033[0m'
                    except Exception, e:
                        pass
                    else:
                        pass
                    finally:
                        pass


# 判断返回内容是否是半角字符
# def is_alphabet(uchar):   
#     try:
#         if (u'\u0041' <= uchar<=u'\u005a') or (u'\u0061' <= uchar<=u'\u007a'):
#             return True
#             # print '英文'
#         else:
#             return False
#             # print '非英文'
#     except:
#         return False
#         # print '非英文'

printLock = threading.Lock()

# 开始主处理class
class webmap(threading.Thread):
    def run(self):
        try:
            ports=args.port.split(',')
            while ipQueue.qsize()>0:
                ip=ipQueue.get()
                for port in ports:
                    try:
                        r=requests.Session().get('http://'+str(ip)+':'+port, headers=header, timeout=TimeOut)
                        r.encoding = 'utf-8'
                        status=r.status_code
                        content=r.text
                        title=re.search(r'<title>(.*)</title>', content)
                        if title:
                            title=title.group(1).strip().strip('\r').strip('\n')
                        else:
                            title='None'
                        try:
                            server=r.headers['Server']
                        except:pass

                        try:
                            printLock.acquire()
                        except:
                            print '一次异常'
                        else:
                            print '''
%s:%s
  └ Status: %s
  └ Sever: %s
  └ Title: %s               ''' % (ip,port,status,server,title)

                            file='./'+args.ip+'.html'
                            with open(file,'a') as f:
                                f.write('''<!DOCTYPE html>
<p>
<a href="http://%s:%s" target="_blank">%s:%s</a><br>
<font size=2>
  └ Status:%s<br>
  └ Sever: %s<br>
  └ Title: %s<br>
</font>
</p>'''%(ip,port,ip,port,status,server,title))
                            # 这里需要改为生成html文件
                            
                            printLock.release()
                        finally:
                            printLock.release()

                    except Exception:
                        pass
                    finally:
                        pass
        except:pass

# 测试函数
def test():
    while ipQueue.qsize()>0:
        print ipQueue.get()
    print '\nargs.thread: '+ str(args.thread)

# 处理自定义多线程
def multithreading(thread_num):
    for x in xrange(int(thread_num)):
        t=webmap()
        t.start()

# main()
ip=args.ip
if __name__ == '__main__':
    if ip.find('-')>=0:
        iplist=get_ip(ip)
        iplist2queue()
    elif ip.find('/')>=0:
        ip=ip.split("/")
        iplist=IPy.IP(ip[0]).make_net('255.255.255.0')
        iplist2queue()
    else:
        try:
            ip=domain2ip(ip)
            if ip:
                ip=IPy.IP(ip).make_net('255.255.255.0')
                iplist=IPy.IP(ip)
                iplist2queue()
        except Exception, e:
            pass
    try:
        multithreading(args.thread)
    except:pass






# 方便下翻