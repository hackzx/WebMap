# encoding: UTF-8
import argparse
import requests
import gevent
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

TimeOut=5

header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36','Connection':'close'}

parser=argparse.ArgumentParser(prog='dirScan', description='''
NIXI dirScan v0.1  用於直接掃描敏感文件

''', epilog='本來是想集成到WebMap中的，然而效率大大降低，所以乾脆拿出來先弄成單獨的腳本，以後再合併吧。\
')
parser.add_argument('ip', help='不要 http://')
parser.add_argument('-d', '--dict', help='指定目錄字典文件', default='dict')
parser.add_argument('-p', '--port', help='自定义端口，默认80', metavar='port', default='80')
args=parser.parse_args()

def dirScan(ip, port, line):
    try:
        url = 'http://' + ip + ':' + port + '/' + line
        r=requests.Session().head(url, headers=header, timeout=TimeOut, allow_redirects=False)
        if r.status_code == 200:
            print '\033[32m' + '         └ [%d]/%s' % (r.status_code, line) + '\033[0m'
            f.write('''<font size=1 face='Monaco'>
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; └ <a href="http://%s:%s/%s" target="_blank">[%s]%s<a>
</font>
''' % (ip,port,line,r.status_code,line))
        elif r.status_code == 403:
            print '\033[33m' + '         └ [%d]/%s' % (r.status_code, line) + '\033[0m'
            f.write('''<font size=1 face='Monaco'>
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; └ <a href="http://%s:%s/%s" target="_blank">[%s]%s<a>
</font>
''' % (ip,port,line,r.status_code,line))
        elif r.status_code == 500:
            print '\033[1;36m' + '         └ [%d]/%s' % (r.status_code, line) + '\033[0m'
            f.write('''<font size=1 face='Monaco'>
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; └ <a href="http://%s:%s/%s" target="_blank">[%s]%s<a>
</font>
''' % (ip,port,line,r.status_code,line))
    except Exception, e:pass
        # print e

file = args.ip + '.html'
dir=[]
def file2list():
    with open(args.dict, 'r') as dict:
        for line in dict.readlines():
            line=line.strip('\n').strip('\r')
            dir.append(line)
    while '' in dir:
        dir.remove('')

def run():
    print '  └ Found: Sensitive Dir'
    p = Pool(100)
    for line in dir:
        p.spawn(dirScan, args.ip, args.port, line)
    p.join()

if __name__ == '__main__':
    with open(file, 'a') as f:
        f.write('%s:%s' % (args.ip, args.port))

        file2list()
        run()
