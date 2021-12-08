# coding=utf-8
from com import utils
from hashlib import md5
import choices

"营销中台任务模型"

bson = {
    "name":  (1, u'', None, u'任务名称'),
    "nums":  (0, 0, None, u'任务运行次数'),
    "source_type":  (0, u'', None, u'数据源类型'), # 1:api;2:数据源;3:excel
    "source_id":  (0, u'', None, u'数据源ID'),
    "source_name":  (0, u'', None, u'数据源名称'),
    "source_table":  (0, u'', None, u'数据源表名'),
    "spider_groupid":  (0, u'', None, u'爬虫组ID'),
    "spider_list":  (0, [], None, u'爬虫设置列表'),
    "dest_tablename":  (0, u'', None, u'入湖表'),
    "dest_table":  (0, u'', None, u'入湖表名'),
    "where":  (0, u'', None, u'查询条件'),
    "update_type":  (0, 0, None, u'更新方式'), #0全量;1增量
    "run_type":  (0, 0, None, u'执行方式'), #1手动;2自动
    "run_hour":  (0, 0, None, u'每日执行时间'),
    "last_runtime": (0, None, utils.re.daytime, u'最后运行时间'),
    "last_status": (0, 0, None, u'最后执行状态'), #　-1异常， 0未执行，１执行中，２执行完成　
    "last_exception": (0, u'', None, u'最后异常描述'),

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