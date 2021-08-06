#!/usr/bin/env python
# -*- coding:utf-8-*-

import requests
import Queue
import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool


TimeOut=5
header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36','Connection':'close'}

def alive(domain):
	try:
		r=requests.Session().get('http://'+str(domain), headers=header, timeout=TimeOut)
		r.encoding = 'utf-8'
		status=r.status_code
		if status:
			print domain
	except Exception as e:
		raise e

def run():
    p = Pool(100) #限制並發數 
    while ipQueue.qsize()>0:
        p.spawn(alive, ipQueue.get())
    p.join()

dir=[]
def file2list():
    with open('subDomainsList', 'r') as dict:
        for line in dict.readlines():
            line=line.strip('\n').strip('\r')
            dir.append(line)
    while '' in dir:
        dir.remove('')

ipQueue=Queue.Queue()
def list2queue():
    for x in dir:
        x=str(x)
        ipQueue.put(x)

if __name__ == '__main__':
	file2list()
	list2queue()
	try:
		run()
	except Exception as e:
		raise e
