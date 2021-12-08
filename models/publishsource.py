# coding=utf-8
from com import utils
from hashlib import md5
import choices

"publish_missions"

bson = {
    "userid": (0, u'', None, u'userid'),
    "openid":  (0, u'', None, u'用户唯一标识'),
    "type": (0, u'', None, u'类型  1：抖音  2：快手'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'上传时间'),
    "source_id":(0, u'', None, u'分发平台资源id'),
    "video_id":(0, u'', None, u'上传视频生成的平台视频id'),
    "error_code":(0, u'', None, u'错误代码'),
    "description":(0, u'', None, u'错误描述'),
    "item_id":(0, u'', None, u'平台的创建视频唯一标识'),
    "title":(0, u'', None, u'发布的视频标题'),
    "cover": (1, u'', None, u'封面图片本地路径'),
    "share_url": (0, u'', None, u'播放路径'),
    "video_status": (0, u'', None, u'视频状态'),
    "create_time": (0, u'', None, u'创建时间'),
    "is_top": (0, u'', None, u'是否置顶'),
    "statistics":(0, u'', None, u'statistics json 数据结构'),
    "platform":(0, u'', None, u'是否短视频平台自行上传 1是0否'),

}

index = {

}