# coding=utf-8
from com import utils
from hashlib import md5
import choices

"百度观星盘数据模型"

bson = {
    "first_name":  (0, u'', None, u'一级行业'),
    "second_name":  (0, u'', None, u'二级行业'),
    "province":  (0, u'', None, u'省份'),
    "city":  (0, u'', None, u'城市'),
    "date":  (0, u'', None, u'日期'),
    "source":  (0, u'', None, u'来源'),
    "trend":  (0, u'', None, u'检索量'),

    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'首次记录时间'),
    "adder":   (0, u'', None, u'首次记录人'),
    "adderip": (0, u'0.0.0.0', utils.re.ipaddr, u'首次记录来源IP地址'),
    "status":  (0, 200, choices.STATUS, u'状态'),
}

index = {

}