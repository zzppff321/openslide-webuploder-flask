# coding=utf-8
from com import utils
from hashlib import md5
import choices

"账户集合模型"

bson = {
    "wxid":     (1, u'', None, u'企业微信ID'),
    "uuid":     (1, u'', utils.re.cardid, u'唯一身份证号码'),
    "account":  (1, u'', None, u'用户名'),
    "passwrd":  (0, u'', None, u'密码'),
    "realname": (0, u'', None, u'真实姓名'),
    "pinyin":   (0, u'', None, u'姓名拼音'),
    "gender":   (0, 1,   None, u'性别，1-男；2-女'),
    "mailbox":  (0, u'', utils.re.mailbox, u'邮箱地址'),
    "mobile":   (1, u'', utils.re.mobile, u'手机号码'),
    "location": (0, u'', None, u'工作地点（省份）'),
    "depart":   (0, u'', None, u'职能'),
    "level":    (0, 0,   choices.USER_LEVEL, u'主管等级'),
    "leader1":  (0, u'', None, u'专项主管'),
    "leader2":  (0, u'', None, u'部门主管'),
    "leader3":  (0, u'', None, u'部门总监'),
    "leader4":  (0, u'', None, u'体系主管'),
    "leader5":  (0, u'', None, u'公司主管'),
    "rights":   (0, u'', None, u'权限标识'),
    "face":     (0, u'', None, u'头像文件'),
    "addtime":  (0, utils.dt.msecdate, None, u'首次记录时间'),
    "adderip":  (0, u'0.0.0.0', utils.re.ipaddr, u'首次记录来源IP地址'),
    "status":   (0, 200, choices.STATUS, u'状态'),
}

index = {
    "default": {
        "realname": 1,
        "status": -1
    },
    "addtime": {
        "addtime": 1
    }
}

default = ({
    "uuid":     u'210000000000000000',
    "account":  u'admin',
    "passwrd":  md5(u'admin').hexdigest(),
    "realname": u'超级管理员',
    "mailbox":  u'advice@panguweb.cn',
    "mobile":   u'18600000000',
    "depart":   u'D',
    "level":    -1,
    "rights":   {},
    "addtime":  utils.dt.msecdate(),
    "adderip":  u'0.0.0.0',
    "status":   200
},)

from com.db import SequoiaDB
class func(SequoiaDB.Q):
    def levelstr(self):
        for k, v in choices.USER_LEVEL:
            if k == self.level:
                return v
                break
        return u'待授权'
