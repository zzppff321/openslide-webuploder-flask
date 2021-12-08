# coding=utf-8
from com import utils
from hashlib import md5
import choices

"任务执行日志模型"

bson = {
    "pid":  (0, u'', u'', u'任务ID'),
    "spiderid":  (0, u'', u'', u'爬虫名字'),
    "spiderurl":  (0, u'', u'', u'爬虫URL'),
    "spiderparam":  (0, u'', u'', u'爬虫参数'),
    "where":  (0, u'', u'', u'查询条件'),
    "update_type":  (0, 0, None, u'更新方式'), #0全量;1增量　
    "runstatus": (0, 0, None, u'执行状态'), #　-1异常， 0未执行，１执行中，２执行完成　
    "exception": (0, u'', None, u'异常描述'),
    "updtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后更新时间'),
    "upder":   (0, u'', None, u'最后更新人'),
    "upderip": (0, u'0.0.0.0', utils.re.ipaddr, u'最后更新来源IP地址'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'首次记录时间'),
    "adder":   (0, u'', None, u'首次记录人'),
    "adderip": (0, u'0.0.0.0', utils.re.ipaddr, u'首次记录来源IP地址'),
    "status":  (0, 200, choices.STATUS, u'状态'),
}

index = {
    "addtime": {
        "addtime": 1
    }
}