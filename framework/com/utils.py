# coding=utf-8
import datetime, time
import re as regex
from flask import Response

class _regex():
    cardid  = r'^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X)$'
    ipaddr  = r'((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|[0-9])(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)){3}'
    domain  = ur'^[0-9a-zA-Z\-_\u4e00-\u9fa5]{1,62}\.([0-9a-zA-Z]{2,20}|[\u4e00-\u9fa5]{2,4})[\.a-zA-Z]{0,4}$'
    mailbox = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    mobile  = r'^(1[3456789]{1}[0-9]{1})+\d{8}$'
    phone   = r'^((\d{4})?(\-)?\d{7,8}|\d{3}\-\d{6}|(\d{3}\-\d{7}-\d{3}))$|%s' % mobile
    daytime = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

    def invalid(self, value, rule):
        if hasattr(self, rule): rule = getattr(self, rule)
        if regex.match(rule, value) is None: return True
        return False

re = _regex()

class _datetime():
    def msecdate(self):
        return datetime.datetime.now()
    def daydiff(self, dt, day=1):
        #时间相加
        #？？？datetime没有“秒”的计算，需要修改成time方法
        return dt + datetime.timedelta(days=day)
    def timestamp(self):
        return int(time.time()*1000000)
    def stamp2time(self, stamp):
        return time.strftime( '%Y-%m-%d %X', time.localtime(stamp/1000000) )
    def strpdate(self, stime):
        #？？？pdata用于转换日期格式
        try:
            return datetime.datetime.strptime( stime, '%Y-%m-%d %H:%M:%S.%f' )
        except:
            return None
    def strptime(self, stime):
        try:
            return datetime.datetime.strptime( stime, '%Y-%m-%d %H:%M:%S.%f' )
        except:
            return None

dt = _datetime()

class _format():
    def location(self, code):
        loc = 0
        if   code[:4] in ('1304','1305','1306','1310','1311'): loc = code[:4]
        elif code[:2] in ('13','21','22'): loc = code[:2]
        return loc

ft = _format()

def get_ipaddress(request):
    #获取当前用户的IP地址
    try:
        ip = request.remote_addr
    except:
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0]
        except:
            try:
                ip = request.META['REMOTE_ADDR']
            except:
                ip = '-.-.-.-'
    return ip

#汉字转拼音
from com.pinyin import Pinyin
def pinyin(string):
    #转换字符为拼音
    py = Pinyin()
    return py.pinyin(string)

import json as pythonjson
class _json():
    def request(self, data):
        #转json字符串为字典格式
        args = pythonjson.loads(data)
        data = {}
        for k,v in args.items():
            if type(v) in (str,int): data[k] = str(v).strip()
            elif v is not None: data[k] = v
        return data

    def response(self, data):
        #转换对象或字典为json格式
        return Response(pythonjson.dumps(data), mimetype='application/json')

json = _json()