# coding=utf-8
from com import utils
from hashlib import md5
import choices

"爬虫模型"

bson = {
    "name":  (0, u'', None, u'爬虫名'),
    "gid":  (0, u'', None, u'组ID'),
    "gname":  (0, u'', None, u'组名'),
    "url":  (0, u'', None, u'爬虫URL'),
    "desc":  (0, u'', None, u'描述'),
    "worked":  (0, u'', None, u'工作状态'), # 0－空闲中;1-工作中

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
