# coding=utf-8
from com import utils
import choices

"资源集合模型"

bson = {
    "ipaddr":   (1, u'', None, u'服务器公网IP地址'),
    "lanip":    (0, u'', None, u'局域网IP地址'),
    "brief":    (0, u'', None, u'名称/摘要/标题'),
    "plat":     (0, u'', None, u'服务器放置地点；盘古联通机房,百度云,阿里云,腾讯云,华为云,其他；'),
    "env":      (0, u'', None, u'操作系统；设定可选项，以文字保存'),
    "vir":      (0,   0, None, u'是否虚拟化；0-否;1-是;'),
    "passwd":   (0, u'', None, u'Administrator/root的密码，也可以是证书明码文件内容'),
    "port":     (0, u'', None, u'ssh/terminal的端口号，如：Windows系统的远程做面就记录成“terminal:3389”'),
    "sa":       (0, u'', None, u'管理员姓名'),
    "idrac":    (0, u'', None, u'远程管理地址和端口；硬件管理级别的，不是系统的管理'),
    "hardware": (0, u'', None, u'服务器型号及配置'),
    "remark":   (0, u'', None, u'备注'),

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
        "sn": 1,
        "status": -1
    },
    "classid": {
        "classid": 1
    }
}
