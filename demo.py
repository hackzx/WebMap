import requests
import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

# def webmap(ip):
#     # do someting
#     pass

# ipQueue = ['127.0.0.1', '127.0.0.2']

# def run():
#     p = Pool(100)
#     for i in ipQueue:
#         p.spawn(webmap, i)
#     p.join()



def webmap(ip):
    try:
        url = '{0}/weaver/bsh.servlet.BshServlet'.format(ip)
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            print(url, r.status_code)
    except:
        pass
# ipQueue = ['127.0.0.1', '127.0.0.2']

with open('fanweioaresult.txt') as f:
    ipQueue = f.readlines()

def run():
    p = Pool(200)
    for i in ipQueue:
        p.spawn(webmap, i.strip())
    p.join()

run()