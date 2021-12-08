# -*- coding: utf-8 -*-
import httplib, traceback, datetime, time, json, calendar
from com import utils
from com.db import SequoiaDB

class Statis(object):
    def run(self):
        # 获取域名信息
        # 来源：由客户端js程序触发AJAX方式访问
        # 传入：
        #   key: 被搜索的域名
        # 2. 获取外部传入的设置数据
        db = SequoiaDB(logger=False)
        # 3. 查询数据
        s = {"domain": "", "account": "", "passwrd": "", "token": "", "siteid": "", "crmid": ""}
        w = {"status": {"$in": [200, 206]}}
        for q in db.query('statis', s, w):
            cu = None
            for s in db.query('customer', {"maker_id": "", "maker_name": ""},
                                   {"_id": (q.crmid,), "status": {"$in": [200, 206]}}, limit=1):
                cu = s
                break
            try:
                bd_tj = Baidu(q.account, q.passwrd, q.token)
                tm = bd_tj.getTime()
                cr = bd_tj.getData(q.siteid, tm['m_f'], tm['now'], 'month')
                mr = bd_tj.getData(q.siteid, tm['pm_f'], tm['pm_l'], 'month')
                yr = bd_tj.getData(q.siteid, tm['py_f'], tm['py_l'], 'month')
                if cr['msg'] <> "" and mr['msg'] <> "" and yr['msg'] <> "":
                    q.update({"mark": 500}, 0)
                    continue
            except :
                q.update({"mark": 500}, 0)
                continue

            crR = cr['body']['data'][0]['result']['sum'][0][0]
            crO = cr['body']['data'][0]['result']['sum'][0][1]
            mrR = mr['body']['data'][0]['result']['sum'][0][0]
            mrO = mr['body']['data'][0]['result']['sum'][0][1]
            yrR = yr['body']['data'][0]['result']['sum'][0][0]
            yrO = yr['body']['data'][0]['result']['sum'][0][1]
            crR = (crR == '--') and 0.00 or crR
            crO = (crO == '--') and 0 or crO
            mrR = (mrR == '--') and 0.00 or mrR
            mrO = (mrO == '--') and 0 or mrO
            yrR = (yrR == '--') and 0.00 or yrR
            yrO = (yrO == '--') and 0 or yrO
            data = {
                "techer": cu.maker_id,
                "techname": cu.maker_name,
                "crR": crR,
                "crO": crO,
                "mrR": mrR,
                "mrO": mrO,
                "yrR": yrR,
                "yrO": yrO,
            }
            rdata = {
                "dt": tm['m_f'] + '-' + tm['m_l'],
                "techer": cu.maker_id,
                "techname": cu.maker_name,
                "maker_id": u'',
                "maker_name": u'',
                "crR": crR,
                "crO": crO,
                "mrR": mrR,
                "mrO": mrO,
                "yrR": yrR,
                "yrO": yrO,
            }
            q.update(data, 0)
            q.pushed({"record": rdata}, 0)

class Baidu(Statis):
    # 域名
    url = 'api.baidu.com'
    # 获取站点列表的地址
    siteListURI = '/json/tongji/v1/ReportService/getSiteList'
    # 登录的地址
    getDataURI = '/json/tongji/v1/ReportService/getData'
    def __init__(self, user, pwd, token):
        self.pwd = pwd
        self.token = token
        self.user = user
    def getList(self):
        try:
            body = {
                'header': {
                    'account_type': 1,
                    'password': self.pwd,
                    'token': self.token,
                    'username': self.user,
                },
            }
            reqStr = json.dumps(body)
            conn = httplib.HTTPSConnection(self.url, timeout=30)
            conn.request(method='POST', url=self.siteListURI, body=reqStr,)
            response = conn.getresponse()
            res = json.loads(response.read())
            if not res['header']['desc'] == 'success':
                if res['header']['failures'][0]['code'] == 81022:
                    res.update({"msg": u"您输入的账户名不正确！"})
                elif res['header']['failures'][0]['code'] == 8202:
                    res.update({"msg": u"您输入的密码不正确！"})
                elif res['header']['failures'][0]['code'] == 8414:
                    res.update({"msg": u"您输入的token码不正确！"})
                else:
                    res.update({"msg": u"出错了，您输入的数据不合法！"})
            else:
                res.update({"msg": u""})
            return res
        except (IOError, ZeroDivisionError), x:
            traceback.print_exc()

    #siteId:应用的唯一id,通过getlist获取,stime:开始时间,etime:结束时间,gran:时间粒度,支持(day/hour/week/month/year)
    def getData(self,siteId,stime,etime,gran):
        try:
            body = {
                'header': {
                    'account_type': 1,
                    'password': self.pwd,
                    'token': self.token,
                    'username': self.user
                },
                'body': {
                    'siteId': int(siteId),
                    'start_date': stime,
                    'end_date': etime,
                    'method': 'pro/product/a',
                    'metrics': 'cost_count,trans_count',
                    'gran': gran,
                }
            }
            reqStr = json.dumps(body)
            conn = httplib.HTTPSConnection(self.url, timeout=30)
            conn.request(method='POST', url=self.getDataURI, body=reqStr, )
            response = conn.getresponse()
            res = json.loads(response.read())
            if not res['header']['desc'] == 'success':
                res.update({"msg": u"出错了，您输入的数据不合法！"})
            else:
                res.update({"msg": u""})

            return res
        except (IOError, ZeroDivisionError), x:
            traceback.print_exc()

    def getTime(self):
        time = datetime.datetime.now()
        # 求该月第一天
        m_f = datetime.date(time.year, time.month, 1)
        pre_l = m_f - datetime.timedelta(days=1)  # timedelta是一个不错的函数
        pm_f = datetime.date(pre_l.year, pre_l.month, 1).strftime("%Y%m%d")
        monthRange = calendar.monthrange(time.year, time.month)[1]
        py_l = datetime.date(time.year - 1, time.month, monthRange).strftime("%Y%m%d")
        py_f = datetime.date(time.year - 1, time.month, 1).strftime("%Y%m%d")
        m_l = datetime.date(time.year, time.month, monthRange).strftime("%Y%m%d")
        m_f = m_f.strftime("%Y%m%d")
        pm_l = pre_l.strftime("%Y%m%d")
        time_data = {
            'now': time.strftime("%Y%m%d"),
            'm_f': m_f,
            'm_l': m_l,
            'pm_f': pm_f,
            'pm_l': pm_l,
            'py_f': py_f,
            'py_l': py_l,
        }
        return time_data

if __name__ == '__main__':
    pass
