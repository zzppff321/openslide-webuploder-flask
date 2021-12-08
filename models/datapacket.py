# coding=utf-8
from com import utils
from hashlib import md5
import choices

"数据湖集合模型"
bson = {
    "name":  (1, u'', None, u'名称'),
    "tablename":  (0, u'', None, u'集合名称'),
    "source":  (0, u'', None, u'数据源'),

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