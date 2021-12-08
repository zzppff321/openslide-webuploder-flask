#coding=utf-8
import urllib
from hashlib import md5
from xml.dom.minidom import parseString
import time
#用户数字id,用户密码,email

class wInterfaceHandler:
    def __init__(self, client):
        self.client = client

    def newDomain(self, productid, domainname, domainpwd, vyear, address_en, firstname, lastname,
                    organization_en, city, state, address_zh, name, organization_zh, ccity, cstate, manager, organization_type,
                    postcode, country, phone, fax, email, cellphone
                    ):
        timer = time.strftime("%Y%m%d%H%M", time.localtime())
        config = self.client.split('|')
        str = config[0] + config[1] + config[3] + timer
        userstr = md5(str).hexdigest()
        try:
            regtype = 1
            if organization_zh and len(organization_zh) > 4:
                regtype = 2
            params = urllib.urlencode({'userid':int(config[0]), 'userstr':userstr, 'category':u'domain', 'action':u'activate', 'vtime':timer,
                                       'domain':domainname, 'domainpwd':domainpwd, 'vyear':vyear, 'dns1':'dns15.hichina.com', 'dns2':'dns16.hichina.com',
                                       'productid':productid, 'address_en':address_en.encode('gbk'), 'firstname':firstname, 'lastname':lastname,
                                       'organization_en':organization_en, 'city':city, 'state':state,'address_zh':address_zh.encode('gbk'),
                                       'name':name.encode('gbk'), 'organization_zh':organization_zh.encode('gbk'),
                                       'ccity':ccity.encode('gbk'), 'cstate':cstate.encode('gbk'), 'manager':manager.encode('gbk'),
                                       'organization_type':organization_type, 'postcode':postcode, 'country':country, 'phone':phone, 'fax':fax,
                                       'email':email, 'admin_same_as': 2, 'tech_same_as':2 , 'bill_same_as': 2,'regtype':regtype, 'cellphone':cellphone
                                       })
        except Exception as e:
            pass
        f = urllib.urlopen("http://api.hichina.com/wwwnetcn.aspx", params)
        return f.read()
    def renewDomain(self, domainname, deaddate, vyear):
        #万网域名续费接口
        timer = time.strftime("%Y%m%d%H%M", time.localtime())
        config = self.client.split('|')
        str = config[0] + config[1] + config[3] + timer
        userstr = md5(str).hexdigest()
        params = urllib.urlencode({'userid':int(config[0]), 'userstr':userstr, 'category':u'domain', 'action':u'renew', 'vtime':timer,
                                   'domain':domainname, 'deaddate':deaddate, 'vyear':vyear
                                   })
        f = urllib.urlopen("http://api.hichina.com/wwwnetcn.aspx", params)
        # log.info(u'result={}'.format(f.read))
        return f.read()

    def newHost(self, productid, vyear, domain, os, idc, templateid, mail, company, webname, autoresolve):
        #万网空间开通接口
        timer = time.strftime("%Y%m%d%H%M", time.localtime())
        config = self.client.split('|')
        str = config[0] + config[1] + config[3] + timer
        userstr = md5(str).hexdigest()
        params = urllib.urlencode({'userid':int(config[0]), 'userstr':userstr, 'category':u'host', 'action': u'activate', 'productid':productid,
                                   'vtime':timer, 'vyear':vyear, 'domain':domain, 'os':os, 'idc':idc
                                   })
        #sys = SystemProperties()
        #host_interface = sys.system_dics['host_interface']                 #这里将url替换成host_interface
        f = urllib.urlopen("http://api.hichina.com/wwwnetcn.aspx", params)
        # log.info(u'result={}'.format(f.read))
        return f.read()

    def renewHost(self, hostadminid, vyear):
        timer = time.strftime("%Y%m%d%H%M", time.localtime())
        config = self.client.split('|')
        str = config[0] + config[1] + config[3] + timer
        userstr = md5(str).hexdigest()
        params = urllib.urlencode({'userid':int(config[0]), 'userstr':userstr, 'category':u'host', 'action':u'renew',
                                   'vtime':timer, 'hostadminid':hostadminid , 'vyear':vyear
                                   })
        #sys = SystemProperties()
        #host_interface = sys.system_dics['host_interface']                 #这里将url替换成host_interface
        f = urllib.urlopen("http://api.hichina.com/wwwnetcn.aspx", params)
        # log.info(u'result={}'.format(f.read))
        return f.read()

    def newMail(self, productid, vyear, domain, amount, idc, tryout):
        timer = time.strftime("%Y%m%d%H%M", time.localtime())
        config = self.client.split('|')
        str = config[0] + config[1] + config[3] + timer
        userstr = md5(str).hexdigest()
        params = urllib.urlencode({'userid':int(config[0]), 'userstr':userstr, 'category':u'mail', 'action':u'activate',
                                   'vtime':timer, 'productid':productid , 'vyear':vyear, 'domain':domain,
                                   'amount':amount, 'idc':idc, 'tryout':tryout
                                   })
        #sys = SystemProperties()
        #mail_interface = sys.system_dics['mail_interface']                 #这里将url替换成mail_interface
        f = urllib.urlopen("http://api.hichina.com/wwwnetcn.aspx", params)
        # log.info(u'result={}'.format(f.read))
        return f.read()

    def renewMail(self, domain, vyear):
        timer = time.strftime("%Y%m%d%H%M", time.localtime())
        config = self.client.split('|')
        str = config[0] + config[1] + config[3] + timer
        userstr = md5(str).hexdigest()
        params = urllib.urlencode({'userid':int(config[0]), 'userstr':userstr, 'category':u'mail', 'action':u'renew',
                                   'vtime':timer, 'domain':domain, 'vyear':vyear
                                   })
        #sys = SystemProperties()
        #mail_interface = sys.system_dics['mail_interface']                 #这里将url替换成mail_interface
        f = urllib.urlopen("http://api.hichina.com/wwwnetcn.aspx", params)
        # log.info(u'result={}'.format(f.read))
        return f.read()

    def analysor(self, xml):
        xml = xml.replace('encoding="gb2312"', 'encoding="utf-8"')  #接收到的xml文件是gb2312编码，要改成utf-8编码
        temp = unicode(xml,'gb2312')   #然后修改字符串，改为utf-8编码
        xml=temp.encode('utf-8')
        dom = parseString(xml)
        status_node = dom.getElementsByTagName('returncode')[0]
        rc = ''
        sucdate = ''
        deaddate = ''
        hostadminid = ''
        hostpassword = ''
        ipaddress = ''
        error = ''
        db_type = ''
        db_name = ''
        db_ip = ''
        db_user = ''
        db_password = ''
        for node in status_node.childNodes:
            rc = node.data
        if rc == '200':
            try:
                subdate_node = dom.getElementsByTagName('sucdate')[0]
                for node in subdate_node.childNodes:
                    sucdate = node.data
                    sucdate = sucdate[0:4] + '-' + sucdate[4:6] + '-' + sucdate[6:]
                deaddate_node = dom.getElementsByTagName('deaddate')[0]
                for node in deaddate_node.childNodes:
                    deaddate = node.data
            except:
                pass

            try:
                hostadminid_node = dom.getElementsByTagName('hostadminid')[0]
                for node in hostadminid_node.childNodes:
                    hostadminid = node.data
                hostpassword_node = dom.getElementsByTagName('hostpassword')[0]
                for node in hostpassword_node.childNodes:
                    hostpassword = node.data
                ipaddress_node = dom.getElementsByTagName('ipaddress')[0]
                for node in ipaddress_node.childNodes:
                    ipaddress = node.data
                db_type_node = dom.getElementsByTagName('db_type')[0]
                for node in db_type_node.childNodes:
                    db_type = node.data
                db_name_node = dom.getElementsByTagName('db_name')[0]
                for node in db_name_node.childNodes:
                    db_name = node.data
                db_ip_node = dom.getElementsByTagName('db_ipaddress')[0]
                for node in db_ip_node.childNodes:
                    db_ip = node.data
                db_user_node = dom.getElementsByTagName('db_user')[0]
                for node in db_user_node.childNodes:
                    db_user = node.data
                db_password_node = dom.getElementsByTagName('db_password')[0]
                for node in db_password_node.childNodes:
                    db_password = node.data
            except:
                pass
        else:
            try:
                error_node = dom.getElementsByTagName('failreason')[0]
                for node in error_node.childNodes:
                    error = node.data
            except:
                pass
        return [rc, sucdate, deaddate, error, hostadminid, hostpassword, ipaddress, db_type, db_name, db_ip, db_user, db_password]
