# coding=utf-8
from com import utils
import choices

"资源集合模型"

bson = {
    "sn":       (1, u'', None, u'编号'),
    "brief":    (0, u'', None, u'名称/摘要/标题'),
    "category": (0, u'', None, u'所属类别，单选；模版（网站,平面,视频,其他）；'),
    "scene":    (0, u'', None, u'应用场景，多选；'),
    "trade":    (0, u'', None, u'适配行业，多选；'),
    "preview":  (0, u'', None, u'预览图片地址'),
    "example":  (0, u'', None, u'演示地址'),
    "qrcode":   (0, u'', None, u'演示地址二维码'),
    "package":  (0, u'', None, u'源码包地址'),
    "detail":   (0, u'', None, u'详细介绍'),
    "terminal": (0, u'', None, u'支持终端，多选；100-PC；200-移动；201-百度小程序；202-微信小程序；999-其他；'),
    "shape":    (0, u'', None, u'表现形式，多选；模版（素材拼接,拍摄剪辑,动画创意,原生创意,故事剧情,其他）；素材（人物,动物,植物,真实,卡通,虚拟,其他）'),
    "style":    (0, u'', None, u'设计风格，单选；传统,时尚,科技,商业,古典,卡通,休闲,活泼,另类,其他'),
    "color":    (0, [] , None, u'配色方案，多选；[主色, 辅色1, 辅色2, 辅色3]'),
    "creator":  (0, u'', None, u'创意人'),
    "origin":   (0, 0  , ((1,u'是'),(0,u'否')), u'是否原创'),
    "on3d":     (0, 0  , ((1,u'是'),(0,u'否')), u'3D效果'),
    "draw":     (0, 0  , ((1,u'是'),(0,u'否')), u'是否手绘'),
    "label":    (0, [] , None, u'标签，包括：类别中文+场景中文+行业中文+形式中文+风格中文，以及终端中文'),
    "used":     (0, 0  , None, u'正在使用资源内容的数量'),
    "classid":  (0, 0  , None, u'资源种类，1-素材；2-模块；6-方案；7-模版；'),

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
