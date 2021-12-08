# coding=utf-8
from com import utils
import choices

"资源集合模型"

bson = {
    "title":    (0, u'', None, u'任务标题'),
    "brief":    (0, u'', None, u'任务描述'),
    "maker":    (0, u'', None, u'执行人姓名'),
    "maker_wx": (0, u'', None, u'执行人wxid'),
    "leader1":  (0, u'', None, u'执行上级1姓名'),
    "leader2":  (0, u'', None, u'执行上级2姓名'),
    "leader":   (0, [] , None, u'执行上级wxid列表'),
    "sponsor":  (0, u'', None, u'需求提出人姓名'),
    "adderid":  (0, u'', None, u'发起人wxid'),

    "updtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后更新时间'),
    "upder":   (0, u'', None, u'最后更新人'),
    "upderip": (0, u'0.0.0.0', utils.re.ipaddr, u'最后更新来源IP地址'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'首次记录时间'),
    "adder":   (0, u'', None, u'首次记录人'),
    "adderip": (0, u'0.0.0.0', utils.re.ipaddr, u'首次记录来源IP地址'),
    "status":  (0, 200, choices.STATUS, u'状态'),
}

index = {
    "default": {
        "status": -1 #倒序
    },
    "classid": {
        "addtime": 1 #正序
    }
}
