# coding=utf-8
from com import utils
import choices

"资源集合模型"

bson = {
    "sn":       (1, u'', None, u'编号'),
    "brief":    (0, u'', None, u'名称/摘要/标题'),
    "plat":     (0, [] , None, u'集成平台，多选；百度,阿里,腾讯,华为,科大讯飞,其他；'),
    "env":      (0, [] , None, u'支持开发环境，多选；Python,PHP,Java,C/C++,HTML,其他；'),
    "creatid":  (0, u'', None, u'开发者ID'),
    "creator":  (0, u'', None, u'开发者姓名'),
    "svn":      (0, u'', None, u'源码包svn地址'),
    "detail":   (0, u'', None, u'使用说明，大文本'),
    "report":   (0, u'', None, u'报告文件，必须是pdf文件'),
    "label":    (0, [] , None, u'标签，可自定义，用于搜索'),
    "classid":  (0, 0  , None, u'资源种类，1-语音；2-图像；3-数据；0-其他；'),

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
