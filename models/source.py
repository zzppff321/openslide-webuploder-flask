# coding=utf-8
from com import utils
import choices

"素材列表"

bson = {
    "id": (1, u'', None, u'视频id'),
    "pic_path": (1, u'', None, u'封面图片本地路径'),
    "title": (1, u'', None, u'Video title'),
    "video_path": (0, u'', None, u'视频本地路径'),
    "play": (0, u'', None, u'播放次数'),
    "heart": (0, u'', None, u'点赞'),
    "share": (0, u'', None, u'分享'),
    "download": (0, u'', None, u'下载'),
    "comment": (0, u'', None, u'评论'),
    "addtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后使用时间'),
    "updtime": (0, utils.dt.msecdate, utils.re.daytime, u'最后更新时间'),
    "userid":(0, u'', None, u'前台用户userid'),
    "remark":(0, u'', None, u'上传文件备注'),
    "video_website":(0, u'', None, u'短视频平台 tiktok-抖音,kwai-快手'),
    "is_settime":(0, u'', None, u'是否定时任务 1是0否'),
    "settime":(0, u'', '', u'定时任务时间'),
    "media_list":(0, u'', '', u'逗号分隔媒体号 media_id'),
    "publish_status":(0, u'', '', u'发布状态 1已发布 0 未发布'),

}

index = {

}
