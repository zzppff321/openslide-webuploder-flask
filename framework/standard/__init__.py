#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
BLUENAME = 'main'+'FW' #Graphical User Interface
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)

from flask import session
#session.permanent = True

from flask import request, render_template, redirect, flash, url_for
from com.db import SequoiaDB
from com.minerequest import MineManager, MineAuthentic
from com.pinyin import Pinyin

#企业微信（Work weixin）对接类
import requests, json
import config

class _WWX():
    access_token = u''
    def __init__(self, wx_corpid, wx_secret):
        self.wx_corpid = wx_corpid
        self.wx_secret = wx_secret

    def get_accesstoken(self, wx_corpid, wx_secret):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {'corpid': wx_corpid, 'corpsecret': wx_secret}
        #requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        req = s.get(url, params=params)
        result = {}
        if req.status_code == requests.codes.ok:
            result = req.json()
        self.access_token = result['access_token']
        return result['access_token']

    def send_taskcard(self, agentid, userid, card):
        self.get_accesstoken(self.wx_corpid, self.wx_secret)
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % self.access_token
        params = {
            "touser":   userid,
            "toparty":  "",
            "totag":    "",
            "msgtype":  "taskcard",
            "agentid":  agentid,
            "taskcard": card,
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
         }
        req = requests.post(url, json.dumps(params), headers={"Content-Type": "application/json","charset": "utf-8"})
        if req.status_code == requests.codes.ok:
            return req.json()
        else:
            print(u'card:%s' % card, url)

    def get_userid(self, code):
        self.get_accesstoken(self.wx_corpid, self.wx_secret)
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
        req = requests.get(url, params={"access_token":self.access_token, "code":code})
        if req.status_code == requests.codes.ok:
            return req.json()

    def get_userinfo(self, userid):
        self.get_accesstoken(self.wx_corpid, self.wx_secret)
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
        req = requests.get(url, params={"access_token":self.access_token, "userid":userid})
        if req.status_code == requests.codes.ok:
            return req.json()
            return req.json()
WWX = _WWX(config.wechat['CORPID'], config.wechat['CORPSECRET'])

#企业微信登录验证（登录时自动注册）
def entry_wwx():
    code  = request.args.get('code',  u'')
    state = request.args.get('state', u'')
    appid = request.args.get('appid', u'')
    
    if code == u'' or appid == u'': return redirect("/")
    
    wxid = None
    wxinfo = WWX.get_userid(code)
    if wxinfo['errcode'] == 0:
        wxid = wxinfo['UserId']
    else:
        flash(u'数据故障：%s，请稍后再试！' % wxinfo, 'error')
        return redirect("/")

    wxinfo = WWX.get_userinfo(wxid)
    if wxinfo['errcode'] != 0:
        flash(u'信息故障，请稍后再试！', 'error')
        return redirect("/")
    if wxinfo['status'] != 1:
        flash(u'您的企业微信帐号未激活，请联系人力资源了解详情！', 'error')
        return redirect("/")
    if wxinfo['enable'] != 1:
        flash(u'您的企业微信帐号未启用，请联系人力资源了解详情！', 'error')
        return redirect("/")

    db = SequoiaDB()
    #微信账户有效，需要将微信账户与系统账户对应
    select = MineManager._select #{"status":"", "realname": "", "depart": "", "level": "", "status": "", "location": ""}
    # where  = {"wxid":wxid}
    where  = {"realname":u"王海涛"}

    query = None
    for q in db.query("users", select, where, {}, limit=1):
        print q
        query = q
        break
    #如果微信账户第一次登录或者被强制删除系统账户，则需要录入账户信息
    if query is None:
        py = Pinyin()
        data = {
            u"wxid":    wxinfo["userid"],
            u"uuid":    u"9"+u"0"*(17-len(wxinfo["mobile"]))+wxinfo["mobile"],
            u"account": u"wx_%s" % wxinfo["userid"],
            u"pasword": u"",
            u"realname":wxinfo["name"],
            u"pinyin":  py.pinyin(wxinfo["name"]),
            u"gender":  wxinfo["gender"],
            u"mailbox": wxinfo["email"],
            u"mobile":  wxinfo["mobile"],
            u"depart":  wxinfo["department"],
            u"face":    wxinfo["avatar"],
            u"status":  405 #默认新用户需要审核后才可以使用系统
        }
        db.insert(request, "users", data=data, event_desc=(1000, u'企业微信新用户'), laissez_passer=[u'uuid'])
        ##添加后再查询，效率不高。？？？
        for q in db.query("users", select, where, {}, limit=1):
            query = q
            break
    
    if query.status == 405:
        flash(u'您的账户还在审核的路途中，请耐心等待！', 'error')
        return redirect("/")
    if query.status != 200:
        flash(u'您的账户被锁定，请尽快联系管理员！', 'error')
        return redirect("/")
    #所有验证完毕，账户一定合法
    Mine = MineManager(request, wwx_user=query)

    if Mine.message is not None:
        flash(u'账户异常：%s' % Mine.message, 'error')
        return redirect("/")

    return redirect("/")

#登录验证
@mod.route('entry', methods=['GET','POST'])
def entry():
    #用户的退出行为
    if request.method == "GET" and 'out' in request.args:
        #表示退出
        Mine = request.Mine()
        Mine.close(request)

        return redirect('/')#'{"method": 0, "status": 200}'
    #用户的企业微信扫码登录
    return entry_wwx()

#系统首页
@mod.route('', methods=['GET'])
def homepage():
    Mine = request.Mine()
    print Mine.is_online
    if Mine.is_online:
        HTML = render_template('main.html', Mine=Mine)
        return HTML
    else:
        if request.url.startswith('http://'): flash(u'您正在使用测试服务，请使用HTTPS协议的正式系统！', 'error')
        HTML = render_template('login.html')
        return HTML

#系统控制台
@mod.route('console', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=0, depict=u'数据仪表') #uid为0，表示任何人都可以使用
def opera_console():
    Mine = request.Mine()

    if request.method == 'POST':
        html = u'<ul class="bar">%s%s</ul>'
        _before = u'00'
        firsted = False

        for ri in MineAuthentic.getlist():
            if not Mine.level == -1 and ri[0] not in Mine.rights: continue
            if ri[0] == 0 or ri[5] is None: continue
            if not str(ri[0])[:2] == _before:
                try:
                    url = url_for(ri[6])
                except:
                    url = u''
                node = u'''<li>
  <a id="%s" href="%s" icon="/images/%s.gif" target="%s" class="node%s" title="%s">%s</a>
  %s
</li>
%s''' % (ri[0], url, ri[3], ri[4], ri[5], ri[2], ri[1], u'%s', u'%s')
                html = html % (u'', node)
                firsted = True
            else:
                try:
                    url = url_for(ri[6])
                except:
                    url = u''
                if firsted: html = html % (u'<ul>%s</ul>', u'%s')
                node = u'''<li><a id="%s" href="%s" icon="/images/%s.gif" target="%s" title="%s">%s</a></li>
    %s''' % (ri[0], url, ri[3], ri[4], ri[2], ri[1], u'%s')
                html = html % (node, u'%s')
                firsted = False
            _before = str(ri[0])[:2]

        return html % (u'', u'')

    return u'常用的控制台和主要数据仪表'
