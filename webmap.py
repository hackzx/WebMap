#!/usr/bin/env python
# -*- coding:utf-8-*-
import shutil
import argparse
import IPy
import socket
import Queue
import requests
import re
import os
import gevent
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

TimeOut = 5

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36', 'Connection': 'close'}

parser = argparse.ArgumentParser(prog='WebMap', description='''\
NIXI WebMap v0.2
''', epilog='方便快捷！')
parser.add_argument('ip', help='10.0.0.1-10.0.0.255 or 10.0.0.0/24 or domain.com')
parser.add_argument('-s', '--scan', help='执行简单敏感文件扫描', action='store_true')
parser.add_argument('-d', '--dict', help='指定目錄字典文件', default='dict')
# parser.add_argument('-t', '--thread', metavar='num', help='自定义线程，默认100', default=100)
parser.add_argument('-p', '--port', help='自定义端口，默认全部扫描', metavar='port', default='80,443,808,3000,3700,4000,4848,8080,8009,7001,7676,8000,8008,8088,8888,8808,8081,8090,8091,8443,9000,9001,9002,9043,9060,9080,9090,9443,18080,28080')
# parser.add_argument('-o', '--output', help='輸出到文件', default=args.ip)
args = parser.parse_args()


def ip2num(ip):
    ip = [int(x) for x in ip.split('.')]
    return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]


def num2ip(num):
    return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                            (num & 0x00ff0000) >> 16,
                            (num & 0x0000ff00) >> 8,
                            num & 0x000000ff)


def get_ip(ip):
    start, end = [ip2num(x) for x in ip.split('-')]
    return [num2ip(num) for num in range(start, end + 1) if num & 0xff]


def domain2ip(domain):
    try:
        # result = socket.getaddrinfo(domain, None)
        # return result[0][4][0]
        return socket.gethostbyname(domain)
    except:
        return 0


ipQueue = Queue.Queue()


def iplist2queue():
    for x in iplist:
        x = str(x)
        ipQueue.put(x)


def webmap(ip):
    try:
        ports = args.port.split(',')
        for port in ports:
            r = requests.Session().get('http://' + str(ip) + ':' + port, headers=header, timeout=TimeOut)
            r.encoding = 'utf-8'
            status = r.status_code
            content = r.text
            title = re.search(r'<title>(.*)</title>', content)
            if title:
                title = title.group(1).strip().strip('\r').strip('\n')
            else:
                title = 'None'
            try:
                server = r.headers['Server']
            except:
                pass
            print '''
%s:%s
  └ Status: %s
  └ Sever: %s
  └ Title: %s               ''' % (ip, port, status, server, title)
            title = title.replace('<', '&lt;').replace('>', '&gt;')
            file = './' + output + '.html'
            with open(file, 'a') as f:
                f.write('''<!DOCTYPE html>
<p>
<a href="http://%s:%s" target="_blank">%s:%s</a><br>
<font size=1 face='Monaco'>
  └ Status:%s<br>
  └ Sever: %s<br>
  └ Title: %s<br>
</font>

''' % (ip, port, ip, port, status, server, title))
    except:
        pass
    # except Exception, e:raise e


dir = []


def file2list():
    with open(args.dict, 'r') as dict:
        for line in dict.readlines():
            line = line.strip('\n').strip('\r')
            dir.append(line)
    while '' in dir:
        dir.remove('')


def run():
    p = Pool(100)  # 限制並發數
    while ipQueue.qsize() > 0:
        p.spawn(webmap, ipQueue.get())
    p.join()


if __name__ == '__main__':
    ip = args.ip
    output = args.ip.replace('/', '-')
    if ip.find('-') >= 0:
        iplist = get_ip(ip)
        iplist2queue()
    elif ip.find('/') >= 0:
        ip = ip.split("/")
        iplist = IPy.IP(ip[0]).make_net('255.255.255.0')
        iplist2queue()
    else:
        try:
            ip = domain2ip(ip)
            if ip:
                ip = IPy.IP(ip).make_net('255.255.255.0')
                iplist = IPy.IP(ip)
                iplist2queue()
        except:
            pass
    try:
        run()
    except:
        pass
    shutil.copy(output + '.html', 'index.html')
