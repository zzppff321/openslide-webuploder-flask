# coding=utf-8
from com import utils
import choices

"数据湖，百度搜索量集合模型"

bson = {
    "pid":      (0, u'', None, u'爬虫的唯一编号'),
    "province": (0, u'', None, u'省份'),
    "city":     (0, u'', None, u'城市'),
    "trade1":   (0, u'', None, u'一级行业'),
    "trade2":   (0, u'', None, u'二级行业'),
    "dt":       (0, u'', utils.re.daytime, u'日期'),
    "yy":       (0, u'', None, u'年'),
    "mm":       (0, u'', None, u'月'),
    "dd":       (0, u'', None, u'日'),
    "terminal": (0, 999, None, u'来源终端；100-PC；200-移动；999-其他；'),
    "flow":     (0,   0, None, u'搜索量'),

    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'首次记录时间'),
    "adder":   (0, u'', None, u'首次记录人'),
    "adderip": (0, u'0.0.0.0', utils.re.ipaddr, u'首次记录来源IP地址'),
    "status":  (0, 200, choices.STATUS, u'状态'),
}

index = {
    "default": {
        "dt": 1,
        "status": -1
    },
    "terminal": {
        "terminal": 1
    }
}
