# encoding: utf-8
# coding=utf-8
#-*- coding:utf-8 -*-
import socket, httplib, urllib
import datetime
from xml.etree import ElementTree as xmlet
from urlparse import urlparse
#from com.dns import resolver

class Host:
    #虚拟主机工具
    pass
class Whois:
    #获取域名设置的DNS服务器地址, wanght-2017-9-19
    CNNIC = 'whois.cnnic.net.cn'
    ICANN = 'whois.crsnic.net'
    ORGIC = 'whois.publicinterestregistry.net'
    GLOBL = 'whois.onlinenic.com'
    def connect(self, host, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        faild = 0
        while True:
            try:
                if faild <= 3:
                    s.connect((host, 43))
            except socket.error:
                faild +=1
            else:
                break
                print('Search time out.')
        data = data.decode('gb2312').encode('utf8')
        response = ''
        try:
            s.send(data)
        except:
            return response
        while True:
            try:
                d = s.recv(4096)
            except:
                d = None
            if not d: break
            response += d
        s.close()
        #print(response)
        return response

    def from_icann(self, domain, original_domain):
        #国际域名：.com/.net/.edu
        suffix = domain.split('.')[-1]
        if suffix not in ('com','net','edu','org',): return (None,None,None)
        data = '%s\r\n' % domain
        if suffix in ('org',):
            response = self.connect(self.ORGIC, data)
        else:
            response = self.connect(self.ICANN, data)
        #找出到期时间
        exp = None
        _re = 'Registry Expiry Date:'
        s, e = (response.find(_re), response.find('\n', response.find(_re)))
        try:
            if s > 0: exp = datetime.datetime.strptime( response[s+len(_re):e].strip(), '%Y-%m-%dT%H:%M:%SZ' )
        except:
            exp = None
            print("** time is faild. [%s]%s" % (response[s+len(_re):e].strip(), domain))
        #找出DNS设置
        dns = ''
        _re = 'Name Server:'
        s, e = (response.find(_re), response.find('\n', response.find(_re)))
        if s > 0: dns = response[s+len(_re):e].strip()

        return (original_domain, exp, dns.lower())

    def from_cnnic(self, domain, original_domain):
        #中国域名：.cn
        if domain.split('.')[-1] not in ('cn',): return (None,None,None)
        data = '%s\r\n' % domain
        response = self.connect(self.CNNIC, data)
        #找出到期时间
        exp = None
        _re = 'Expiration Time:'
        s, e = (response.find(_re), response.find('\n', response.find(_re)))
        try:
            if s > 0: exp = datetime.datetime.strptime( response[s+len(_re):e].strip(), '%Y-%m-%d %H:%M:%S' )
        except:
            exp = None
            print("** time is faild. [%s]%s" % (response[s+len(_re):e].strip(), domain))
        #找出DNS设置
        dns = ''
        _re = 'Name Server:'
        s, e = (response.find(_re), response.find('\n', response.find(_re)))
        if s > 0: dns = response[s+len(_re):e].strip()

        return (original_domain, exp, dns.lower())

    def use_global(self, domain, original_domain):
        #其他域名
        data = '%s\r\n' % domain
        response = self.connect(self.GLOBL, data)
        #找出到期时间
        exp = None
        _re = 'Expiration Date:'
        s, e = (response.find(_re), response.find('\n', response.find(_re)))
        try:
            if s > 0: exp = datetime.datetime.strptime( response[s+len(_re):e].strip(), '%Y-%m-%dT%H:%M:%SZ' )
        except:
            exp = None
            print("** time is faild. [%s]%s" % (response[s+len(_re):e].strip(), domain))
        #找出DNS设置
        dns = ''
        _re = 'Name Server:'
        s, e = (response.find(_re), response.find('\n', response.find(_re)))
        if s > 0: dns = response[s+len(_re):e].strip()

        return (original_domain, exp, dns.lower())

class Domain(Whois):
    #域名工具
    def test(self): pass
    def __init__(self, url):
        self.original_domain = self.format(url)
        try:
            self.domain = self.original_domain.encode('gb2312')
        except:
            print(self.original_domain)

    def resolve(self, fix='www'):
        #获取域名设置的DNS服务器地址
        addr = []
        ns = resolver.query(self.domain)
        for x in ns.response.answer:
            for dns in x.items:
                addr.append(dns.to_text())
        ns = resolver.query('%s.%s' % (fix, self.domain))
        for x in ns.response.answer:
            for dns in x.items:
                addr.append(dns.to_text())
        return addr

    def whois(self):
        #获取域名设置的DNS服务器地址, wanght-2017-9-19
        suffix = self.domain.split('.')[-1]
        if suffix in ('com','net','edu','org',):
            return self.use_global(self.domain, self.original_domain)
        if suffix in ('cn',):
            return self.use_global(self.domain, self.original_domain)
        return self.use_global(self.domain, self.original_domain)
        #addr = []
        #ns = resolver.query(self.domain, 'NS')
        #for x in ns.response.answer:
        #    for dns in x.items:
        #        addr.append(dns.to_text())
        #return addr

    def available(self):
        #验证域名是否被注册
        #阿里云接口：http://panda.www.net.cn/cgi-bin/check.cgi?area_domain=域名
        try:
            c = httplib.HTTPConnection('panda.www.net.cn', 80, timeout=120)
            uri = '/cgi-bin/check.cgi?%s' % urllib.urlencode({"area_domain":self.domain})
            c.request('GET', uri)
        except:
            return True #默认返回被注册状态
        xml = c.getresponse().read()[39:]
        xml = xml.decode('gbk').encode('utf8')

        tree = xmlet.fromstring(xml)
        code = 0
        orig = 0
        for child in tree:
            if child.tag == 'returncode': code = child.text
            if child.tag == 'original': orig = child.text
        if orig[:3] == '210': return True
        return False

    def format(self, url):
        #域名格式化,去除（http：//，https：//等协议，去除#，/xxx，？xxx等路径和参数）
        #？？？不能完美过滤三级域名地址和非www主机头的域名
        uri = urlparse(url)
        if uri.netloc:
            domain = u'{uri.netloc}'.format(uri=uri)
        else:
            domain = u'{uri.path}'.format(uri=uri)
            if domain.split(u'/'):
                domain = domain.split(u'/')[0]
        if domain[:4] == u'www.':
            domain = domain[4:]
        return domain

if __name__ == "__main__":
    import sys
    d = unicode(sys.argv[1].decode('utf8'))
    d = Domain(d).whois()