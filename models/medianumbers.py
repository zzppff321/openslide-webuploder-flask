# coding=utf-8
from com import utils
from hashlib import md5
import choices

"媒体号数据"

bson = {
    "openid":  (1, u'', None, u'用户唯一标识'),
    "type": (0, u'', None, u'类型  1：抖音  2：快手'),
    "from_type": (0, u'', None, u'来源  1：平台资源  2：用户资源'),
    "access_token": (0, u'', None, u'token'),
    "refresh_token": (0, u'', None, u'refreshtoken'),
    "parent_id": (0, u'', None, u'父级账号id'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后使用时间'),
    "avatar":(0, u'', None, u'avatar'),
    "nickname":(0, u'', None, u'nickname'),
    "union_id":(0, u'', None, u'union_id'),
    "province":(0, u'', None, u'province'),
    "city":(0, u'', None, u'province'),
    "country":(0, u'', None, u'country'),
}

index = {

}