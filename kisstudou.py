#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import httplib
import re
from HTMLParser import HTMLParser

parser = argparse.ArgumentParser(
        description='Download video resource from tudou.com',
        epilog="Parse the url to video address using flvcd.com")
parser.add_argument('-q', '--quality', 
        default=4, type=int, dest='quality',
        help="""Quality of source to download, 
        values in 0(256P),1(360P),2(480P),3(720P),4(REAL). 
        REAL by default. 
        Note: 
        If the specific resolution is not avaliable the lower nearest will be downloaded""")
parser.add_argument('-o', '--output-pattern', 
        default='%n', dest='pattern',
        help="""Define the output filename format(%%n by default):
        %%n - Video Name.
        %%x - Index of the video in the album.
        %%r - Album name.
        %%p - Video source name.
        """)
parser.add_argument('-w', '--wait', 
        default=2, type=int, dest='wait',
        help="Set the time to wait between start next task(in second, default 2).")
parser.add_argument('-D', '--debug', 
        default=False, dest='debug', action='store_true',
        help="Run command in debug mode")
parser.add_argument('-d', '--new-directory', 
        default=False, dest='mkdir', action='store_true',
        help="Create new directory for the download")
parser.add_argument('-c', '--clean', 
        default=False, dest='clean', action='store_true',
        help="Clean old file before start(for sites unavaliable for partial)")
parser.add_argument('-m', '--merge-split', 
        default=False, dest='merge', action='store_true',
        help="Auto merge videos together(Not Implemented)")
parser.add_argument('-s', '--format-spider', 
        default=False, dest='detect', action='store_true',
        help="Only detect the avaliable format but not download.")
parser.add_argument('-U', '--user-agent', 
        default=r"Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1", 
        dest='ua', 
        help="Specific the User-Agent.")
parser.add_argument('url', help='The URL of the playlist or video')

#arguments here
global args
args = parser.parse_args()

formatLevel = ['normal','high','super','super2','real']
resolution = ['Normal','360P','480P','720P','REAL(DEFAULT)']
parseFormat = {
        'tudou':['256P','360P','480P','720P',u'原画'],
        'youku':[u'标清',u'高清',u'超清','<Unava>','<Unava>'],
        '__default__':[u'标清',u'清晰',u'高清',u'超清',u'原画']
        }
server_info = {
        'partial':['tudou'],
        'retain_addr':['tudou'],
        'split':['youku']
        }

print "Album/video address to parse:"
print args.url
print "Quality:", resolution[args.quality]
print "Pattern:", args.pattern, "+ *ext*"
print 'User-Agent:', args.ua
if args.debug:
    print "Debug:", args.debug
    print "New Dir.:", args.mkdir

def parse(url, ua, fmt):
    http = httplib.HTTP("www.flvcd.com")
    http.putrequest("GET", "/parse.php?format=%s&kw=%s" % (fmt, url))
    http.putheader("User-Agent", ua)
    http.putheader("Host", "www.flvcd.com")
    http.putheader("Accept", "*/*")
    http.endheaders()
    errcode, errmsg, headers = http.getreply()
    print "Status:", errcode, errmsg
    if errcode!=200:
        print "Error encountered while parsing url"
        return -1
    res = http.getfile()
    print 'Parsing video address...'
    html = ''
    data = res.read(512)
    while data != '':
        html += data
        data = res.read(512)
    html = html.decode('gbk')
    return html

html = parse(args.url, args.ua, formatLevel[args.quality])

if html == -1:
    exit(1)

print "Supported format:"
listFormat = [0]
for k, v in parseFormat.items():
    if args.url.find(k)>0:
        for f in xrange(0, len(v)):
            if html.find(v[f])!=-1:
                listFormat.append(f)
        break
print "\t",
for v in listFormat:
    print resolution[v],
print

if args.detect:
    exit(0)

if not args.quality in listFormat:
    while not args.quality in listFormat:
        args.quality = args.quality-1
    print "Real Quality:", resolution[args.quality]
    print "Reparsing the address..."
    html = parse(args.url, args.ua, formatLevel[args.quality])
else:
    print "Quality %s available..." % (resolution[args.quality])

inf_start = '<input type="hidden" name="inf" value="'
inf_end   = """">"""

start = html.index(inf_start)
end   = html.index(inf_end, start)

inf = html[start+len(inf_start):end].encode("utf-8")

if args.debug:
    print "HTML Text:"
    print inf


print 'Get video infomation:'
rl =  inf.strip().replace('<&>\n','').split("<$>\n")

class DownloadItem(object):
    def __init__(self, data):
        self.image = data
    def __getattr__(self, key):
        return re.search('(<'+ key +'>)([^<>]*)\n', self.image).group(2)
    def __str__(self):
        return self.image

album = DownloadItem(rl.pop(0))
print 'Title:', album.R
dl = []
for i in rl:
    dl.append(DownloadItem(i))
print "Found %d items in the list to be downloaded" % len(dl)
print

import os,time

if args.mkdir:
    print 'Creating new dir:', album.R
    os.system('mkdir "%s" 2>/dev/null 1>/dev/null' % album.R)
    os.chdir(album.R)

print 'Current working directory:'
print "\t", os.getcwd()
os.system('''echo "#!/bin/bash
%s -q%s %s \$@" > "%s.to" && chmod +x "%s.to"
        ''' % \
        (__file__,args.quality,args.url,
            album.R.replace('/',"_"),album.R.replace('/',"_")))

def getFileExt(i):
    u = i.U
    if u.find('f4v')!=-1:
        return '.f4v'
    if u.find('mp4')!=-1:
        return '.mp4'
    if u.find('flv')!=-1:
        return '.flv'
    if u.find('hlv')!=-1:
        return '.hlv'
    return ".video"

fSuccess = True

for i in dl:
    local = args.pattern.replace('%n',i.N) \
                .replace('%p',i.P) \
                .replace('%r',album.R) \
                .replace('%x',i.X) \
                .replace('/',"_") \
            + getFileExt(i)

    print "Download", local, "..."
    url = i.U

    if os.path.exists(local):
        print "Target already exists, skip to next file!"
        continue

    rmcmd = "rm -f %s 1>/dev/null 2>/dev/null" % (local+" ."+local)

    if args.clean:
        print "Before we start, clean the unfinished file"
        os.system(rmcmd)

    syscmd = 'wget -c "' + url + '" -U "' + args.ua + '" -O ".' + local + '"' 
    if args.debug:
        print syscmd
        continue

    rtn = os.system(syscmd)
    mvcmd = 'mv "%s" "%s" 1>/dev/null 2>/dev/null' % ('.' + local, local)
    if rtn == 0:
        os.system(mvcmd)
    elif rtn == 2048:
        # Server issued an error response.
        print "Server Error detected, remove part file and retry."
        os.system(rmcmd)
        rtn = os.system(syscmd)
        if rtn == 0:
            os.system(mvcmd)
        else:
            fSuccess = False;
        if rtn == 2048:
            print "Server error again, address may be expired."
            if args.clean:
                os.system(rmcmd)
            continue
    else:
        fSuccess = False;
    time.sleep(args.wait + 0.1)

if fSuccess:
    os.system('rm "%s.to"' % (album.R.replace('/',"_")))

print "All tasks completed."
exit(0)
