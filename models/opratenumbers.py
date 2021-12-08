# coding=utf-8
from com import utils
from hashlib import md5
import choices

"运营账号数据"

bson = {
    "tel":  (1, u'', None, u'电话号码（运营账号）'),
    "password": (0, u'', None, u'登录密码'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后使用时间'),
    "updtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后更新时间'),
    "token":(0, u'', None, u'token令牌'),
}

index = {

}