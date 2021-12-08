# coding=utf-8
from com import utils
from hashlib import md5
import choices

"账户集合模型"

bson = {
    "name":  (1, u'', None, u'用户名'),
    "passwd":  (0, u'', None, u'密码'),
    "gid":  (0, u'', None, u'组ID'),
    "gname":  (0, u'', None, u'组名'),
    "available":  (0, u'', None, u'可用状态'),
    "lastusetime": (0, utils.dt.msecdate, utils.re.daytime, u'最后使用时间'),

    "updtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后更新时间'),
    "upder":   (0, u'', None, u'最后更新人'),
    "upderip": (0, u'0.0.0.0', utils.re.ipaddr, u'最后更新来源IP地址'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'首次记录时间'),
    "adder":   (0, u'', None, u'首次记录人'),
    "adderip": (0, u'0.0.0.0', utils.re.ipaddr, u'首次记录来源IP地址'),
    "status":  (0, 200, choices.STATUS, u'状态'),
}

index = {

}