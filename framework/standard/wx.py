#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
#-*- coding:utf-8 -*-

BLUENAME = 'user_wx'+'AGI' #Application Gateway Interface       #系统内部使用的网关，主要应用于系统需要的ajax读取
#BLUENAME = 'rfs'+'API' #Application Programming Interface   #公共应用接口，主要应用于内外部系统的统一读写操作管理
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)

from flask import session
#session.permanent = True

from flask import request
from com.db import SequoiaDB
from com.pinyin import Pinyin
import config

from com.WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import sys

sToken = "E4ZAS9q5XpFWKXQQUVaiXlkzSL"
sEncodingAESKey = "rT7xDjkH4R2vcih8jEmAcnUohEugIwdmaDgpYkXbE1m"
sCorpID = config.wechat['CORPID']

@mod.route('', methods=['POST', 'GET'])
def opera_main():   #假设企业在企业微信后台设置的参数如下
    wxcpt = WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
    sMsgSig =       request.args.get('msg_signature', u'')
    sTimeStamp =    request.args.get('timestamp', u'')
    sNonce =        request.args.get('nonce', u'')

    if request.method == 'GET':
        '''
        ------------使用示例一：验证回调URL---------------
        *企业开启回调模式时，企业号会向验证url发送一个get请求 
        假设点击验证时，企业收到类似请求：
        * GET /cgi-bin/wxpush?msg_signature=5c45ff5e21c57e6ad56bac8758b79b1d9ac89fd3&timestamp=1409659589&nonce=263014780&echostr=P9nAzCzyDtyTWESHep1vC5X9xho%2FqYX3Zpb4yKa9SKld1DsH3Iyt3tP3zNdtp%2B4RPcs8TgAE7OaBO%2BFZXvnaqQ%3D%3D 
        * HTTP/1.1 Host: qy.weixin.qq.com
        接收到该请求时，企业应	1.解析出Get请求的参数，包括消息体签名(msg_signature)，时间戳(timestamp)，随机数字串(nonce)以及企业微信推送过来的随机加密字符串(echostr),
        这一步注意作URL解码。
        2.验证消息体签名的正确性 
        3. 解密出echostr原文，将原文当作Get请求的response，返回给企业微信
        第2，3步可以用企业微信提供的库函数VerifyURL来实现。
        '''
        sVerifyEchoStr = request.args.get('echostr', u'')
        ret, sEchoStr = wxcpt.VerifyURL(sMsgSig, sTimeStamp, sNonce, sVerifyEchoStr)
        if(ret!=0): return u'',500

        return sEchoStr

    if request.method == 'POST':
        '''
        ------------使用示例二：对用户回复的消息解密---------------
        用户回复消息或者点击事件响应时，企业会收到回调消息，此消息是经过企业微信加密之后的密文以post形式发送给企业，密文格式请参考官方文档
        假设企业收到企业微信的回调消息如下：
        POST /cgi-bin/wxpush? msg_signature=477715d11cdb4164915debcba66cb864d751f3e6&timestamp=1409659813&nonce=1372623149 HTTP/1.1
        Host: qy.weixin.qq.com
        Content-Length: 613
        <xml> <ToUserName><![CDATA[wx5823bf96d3bd56c7]]></ToUserName><Encrypt><![CDATA[RypEvHKD8QQKFhvQ6QleEB4J58tiPdvo+rtK1I9qca6aM/wvqnLSV5zEPeusUiX5L5X/0lWfrf0QADHHhGd3QczcdCUpj911L3vg3W/sYYvuJTs3TUUkSUXxaccAS0qhxchrRYt66wiSpGLYL42aM6A8dTT+6k4aSknmPj48kzJs8qLjvd4Xgpue06DOdnLxAUHzM6+kDZ+HMZfJYuR+LtwGc2hgf5gsijff0ekUNXZiqATP7PF5mZxZ3Izoun1s4zG4LUMnvw2r+KqCKIw+3IQH03v+BCA9nMELNqbSf6tiWSrXJB3LAVGUcallcrw8V2t9EL4EhzJWrQUax5wLVMNS0+rUPA3k22Ncx4XXZS9o0MBH27Bo6BpNelZpS+/uh9KsNlY6bHCmJU9p8g7m3fVKn28H3KDYA5Pl/T8Z1ptDAVe0lXdQ2YoyyH2uyPIGHBZZIs2pDBS8R07+qN+E7Q==]]></Encrypt>
        <AgentID><![CDATA[218]]></AgentID>
        </xml>
        企业收到post请求之后应该 1.解析出url上的参数，包括消息体签名(msg_signature)，时间戳(timestamp)以及随机数字串(nonce)
        2.验证消息体签名的正确性。 3.将post请求的数据进行xml解析，并将<Encrypt>标签的内容进行解密，解密出来的明文即是用户回复消息的明文，明文格式请参考官方文档
        第2，3步可以用企业微信提供的库函数DecryptMsg来实现。
        '''
        sReqData = request.data
        ret, sMsg=wxcpt.DecryptMsg(sReqData, sMsgSig, sTimeStamp, sNonce)
        if(ret!=0): return u'',500
        #？？发送解密后的数据给需要的平台接口

        # 解密成功，sMsg即为xml格式的明文
        # TODO: 对明文的处理
        # For example:
        xml = ET.fromstring(sMsg)

        #获取到推送来的数据之后，就是对数据的处理并保存下来了
        #1. 定义一个函数，用来提取数据中的账户属性
        def gettext(key, val):
            v = xml.find(key)
            if v is None:
                return val
            else:
                return v.text
        #2. 获取几个特定的必要性数据，并开始校对账户的存在性
        sStatus =       gettext("Status", u'0') #基本没有用
        sChangeType =   gettext("ChangeType", u'')
        sUserID =       gettext("UserID", u'')

        if not sChangeType in (u'create_user', u'update_user', u'delete_user'): return u'', 200

        db = SequoiaDB()
        #微信账户有效，需要将微信账户与系统账户对应
        select = {"status":"", "wxid": "", "realname":"","gender":"","mailbox":"","mobile":"","depart":"","face":""}
        where  = {"wxid": sUserID} #这里必须是sUserID，用来查找原来的wxid是否存在
        status = 405

        query = None
        for q in db.query("users", select, where, {}, limit=1):
            # 如果用户存在，并且企业微信的操作是删除用户，则直接修改账户状态为“0”
            if sChangeType == u'delete_user':
                desc = u'通讯录变更时删除账户【%s, %s】的信息' % (q.realname, sUserID)
                q.update({"status":0}, request, event_desc=(1000, desc))
                return desc
            query = q
            status = q.status
            break

        #3. 获取账户的企业微信唯一ID，并针对不存在的账户进行更多数据获取
        wxid = gettext("NewUserID", sUserID)
        mobile,realname,mailbox,gender,depart,face = (None,u'',u'e-%s@panguweb.cn' % wxid,-1,[],u'')

        # 2021年3月17日，因存在mobile等属性位None的情况，所以每次都重新获取一次用户信息，可能会影响性能
        from standard import WWX
        import requests
        WWX.get_accesstoken(WWX.wx_corpid, "qkV9qPGfWzfGOY1W4CqRm1LS51O_J0rniq8Ot_bg7tM")
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
        req = requests.get(url, params={"access_token":WWX.access_token, "userid":wxid})
        if req.status_code == requests.codes.ok:
            jd = req.json()
            mobile   = jd.get("mobile")
            realname = jd.get("name")
            mailbox  = jd.get("email")
            gender   = jd.get("gender")
            depart   = jd.get("department")
            face     = jd.get("avatar")
        # if query is None:
        #     from standard import WWX
        #     import requests
        #     WWX.get_accesstoken(WWX.wx_corpid, "qkV9qPGfWzfGOY1W4CqRm1LS51O_J0rniq8Ot_bg7tM")
        #     url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
        #     req = requests.get(url, params={"access_token":WWX.access_token, "userid":wxid})
        #     if req.status_code == requests.codes.ok:
        #         jd = req.json()
        #         mobile   = jd.get("mobile")
        #         realname = jd.get("name")
        #         mailbox  = jd.get("email")
        #         gender   = jd.get("gender")
        #         depart   = jd.get("department")
        #         face     = jd.get("avatar")

        # #4. 校验数据可用性并加以修正，同时定义一个用于写入的数据结构
        # mobile   = gettext("Mobile", query and query.mobile or mobile)
        # realname = gettext("Name", query and query.realname or realname)
        # mailbox  = gettext("Email", query and query.mailbox or mailbox)
        # gender   = gettext("Gender", gender)
        # depart   = gettext("Department", depart),
        # face     = gettext("Avatar", face),

        if gender is None:
            gender = 0
        else:
            gender = int(gender)
        if mailbox == u'':
            mailbox = u'e-%s@panguweb.cn' % wxid
        if mobile is None:
            print(u'**********')
            print(u'** Data Error : [%s] mobile is none.' % (sUserID))
            print(u'**Request: %s' % sMsg)
        if realname is None:
            print(u'**********')
            print(u'** Data Error : [%s] realname is none.' % (sUserID))
            print(u'**Request: %s' % sMsg)
            return u'', 500
        #验证手机号码是否冲突
        for q in db.query("users", {"status":"", "wxid": ""}, {u'mobile':mobile}, {}):
            if q.wxid == wxid: break #与当前更新账户是同一账户时不用理会
            #冲突账户状态为离职/删除时，可能是是微信账户错误删除后重新开通的新账户，此时应保留原账户并取消新账户
            if q.status == 0:
                if not query is None:
                    status = query.status #状态要更新成原来账户的，如果是新用户，那就还是405
                    query.remove(request, event_desc=(999, u'因手机号码冲突，删除最新的无效账户！'))
                wxid = q.wxid
                query = q
            else: #此时账户状态可能为200、405和403，都是有效的账户状态，？？？还没想好怎么处理
                print(u'**********')
                print(u'** Valid Error : [%s] mobile is exist.' % (sUserID, e))
                print(u'**   Mobi: %s' % mobile)
                print(u'**Request: %s' % sMsg)
                return u'', 500
        #修改姓名和姓名拼音
        for k in ("（", "(", "-", "~"):
            if realname.find(k) > 0: realname = realname[:realname.find(k)]
        py = Pinyin()
        pinyin = py.pinyin(realname)

        data = {
            u"wxid":    wxid,
            u"uuid":    u"9"+u"0"*(17-len(mobile))+mobile,
            u"account": u"wx_%s" % wxid,
            u"pasword": u"",
            u"realname":realname,
            u"pinyin":  pinyin,
            u"gender":  int(gettext("Gender", -1)),
            u"mailbox": mailbox,
            u"mobile":  mobile,
            u"depart":  gettext("Department", []),
            u"face":    gettext("Avatar", u''),
            u"status":  status #默认新用户需要审核后才可以使用系统
        }
        desc = u'done nothing'

        #5. 写入新的未登记系统的账户
        if query is None:
            try:
                desc = u'通讯录变更时导入企业微信用户【%s, %s】' % (data["realname"],wxid)
                db.insert(request, "users", data=data, event_desc=(1000, desc), laissez_passer=[u'uuid'])
            except Exception as e:
                print(u'**********')
                print(u'** Error : [%s] %s' % (sUserID, e))
                print(u'** Insert: %s' % data)
                print(u'**Request: %s' % sMsg)
        else: # 更新已有的账户
            #需要先删除不需要更新的属性，避免一些原始的数据丢失或唯一字段出现冲突
            del data["uuid"]
            del data["pasword"]
            del data["pinyin"]
            try:
                desc = u'通讯录变更时刷新原账户【%s, %s】的信息' % (data["realname"],wxid)
                query.update(data, request, event_desc=(1000, desc))
            except Exception as e:
                print(u'**********')
                print(u'** Error : [%s] %s' % (sUserID, e))
                print(u'** Update: %s' % data)
                print(u'**Request: %s' % sMsg)

        return desc


def demo_sendtoWX(request):
    '''
    ------------使用示例三：企业回复用户消息的加密---------------
    企业被动回复用户的消息也需要进行加密，并且拼接成密文格式的xml串。
    假设企业需要回复用户的明文如下：
    <xml>
    <ToUserName><![CDATA[mycreate]]></ToUserName>
    <FromUserName><![CDATA[wx5823bf96d3bd56c7]]></FromUserName>
    <CreateTime>1348831860</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[this is a test]]></Content>
    <MsgId>1234567890123456</MsgId>
    <AgentID>128</AgentID>
    </xml>
    为了将此段明文回复给用户，企业应： 1.自己生成时间时间戳(timestamp),随机数字串(nonce)以便生成消息体签名，也可以直接用从企业微信的post url上解析出的对应值。
    2.将明文加密得到密文。   3.用密文，步骤1生成的timestamp,nonce和企业在企业微信设定的token生成消息体签名。   4.将密文，消息体签名，时间戳，随机数字串拼接成xml格式的字符串，发送给企业号。
    以上2，3，4步可以用企业微信提供的库函数EncryptMsg来实现。
    '''
    sRespData = "<xml><ToUserName>ww1436e0e65a779aee</ToUserName><FromUserName>ChenJiaShun</FromUserName><CreateTime>1476422779</CreateTime><MsgType>text</MsgType><Content>你好</Content><MsgId>1456453720</MsgId><AgentID>1000002</AgentID></xml>"
    ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, sReqNonce, sReqTimeStamp)
    if( ret!=0 ):
        print "ERR: EncryptMsg ret: " + str(ret)
        sys.exit(1)
    #ret == 0 加密成功，企业需要将sEncryptMsg返回给企业号
    #TODO:
    #HttpUitls.SetResponse(sEncryptMsg)
