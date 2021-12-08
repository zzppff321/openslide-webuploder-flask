# coding=utf-8
from com import utils
import choices

"商品集合模型"

bson = {
    "brief":    (0, u'', None, u'名称/标题/摘要，默认：Resource.sn'),
    "categorid":(0, 0, choices.PRODUCT_CATEGORID, u'商品种类，单选；10-域名/空间；20-网站/小程序；21-落地页；30-视频；70-服务；'),
    "price":    (0, 0.00, None, u'可实际执行的销售价格'),
    "discount": (0, 1.00, None, u'折扣'), #1.00，表示100%，十折

    "resource_id":(0, u'', None, u'资源ID'),
    "sn":       (0, u'', None, u'编号'),
    "trade":    (0, u'', None, u'适配行业，多选；'),
    "preview":  (0, u'', None, u'预览图片地址'),
    "example":  (0, u'', None, u'演示地址'),
    "qrcode":   (0, u'', None, u'演示地址二维码'),
    "terminal": (0, u'', None, u'支持终端，多选；100-PC；200-移动；201-百度小程序；202-微信小程序；999-其他；'),
    "shape":    (0, u'', None, u'表现形式，视频专用，多选；素材拼接,拍摄剪辑,动画创意,原生创意,故事剧情,其他'),
    "style":    (0, u'', None, u'设计风格，单选；传统,时尚,科技,商业,古典,卡通,休闲,活泼,另类,其他'),
    "color":    (0, [] , None, u'配色方案，多选；[主色, 辅色1, 辅色2, 辅色3]'),
    
    "label":    (0, [] , None, u'标签，资源标签+categorid中文'),

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
        "price": 1,
        "status": -1
    }
}

from com.db import SequoiaDB
class func(SequoiaDB.Q):
    def getResource(self, select):
        #根据当前记录的resource_id找出Resource记录对象
        db = SequoiaDB()
        where = {"_id":(self.id,), "status":{"$in":(200,206)}}
        for q in db.query('product', select, where, {}, limit=1):
            return q
        return None
