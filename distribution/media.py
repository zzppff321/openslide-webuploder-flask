#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import time
import hashlib
from com.douyin_openapi import douyinApi
from com.kuaishou_openapi import kuaishouApi
from bson import ObjectId

BLUENAME = 'distribution_media'+'GUI' #Graphical User Interface
from flask import Blueprint

mod = Blueprint(BLUENAME, __name__)

from flask import session
#session.permanent = True

from flask import request, render_template, redirect, url_for
from com.db import SequoiaDB
from com.minerequest import MineAuthentic
from com.sf import StreamFileLocal
from com import utils
import shutil, config

appid = 20200
_var = locals()

@mod.route('', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+10, depict=u'媒体号', menu=10, remark=u'媒体号')
def opera_list():
    Mine = request.Mine()
    db = SequoiaDB()
    if not db.hascl('medianumbers'):
        db.create('medianumbers')
    select = {
        "id":"",
        "openid": "",
        "type": "",
        "from_type": "",
        'access_token':"",
        "refresh_token":"",
        'parent_id':"",
        'addtime':"",
        "nickname":"",
        "avatar":"",
        "total_fans":'',
        'total_issue':''
    }
    # 3.2 组合查询条件
    so = {u'openid': u''}
    # 2.3 获取筛选条件选项的值
    for k, v in so.items():
        _var[k] = so[k] = request.args.get(k, v)
    where = {}
    if request.args.get('parent_id') :
        where['parent_id']=request.args.get('parent_id')
    if request.args.get('type',default='0') != '0':
        where['type']=request.args.get('type')
    if request.args.get('from_type',default='0') != '0':
        where['from_type']=request.args.get('from_type')

    print(openid)
    if not openid == u'':
        where['openid'] =  {"$regex": '%s' % openid}
    # 默认，按添加时间倒序排列，即新用户在前
    orderby = {"addtime": -1}
    query = db.pagebar('medianumbers', select, where, orderby, so)
    for item in query.data:
        item.sourceCount = db.count('publishsource', {"openid":item.openid,"userid": item.parent_id})
    userIdList=[(media.parent_id) for media in query.data]
    userList={user.id:user.tel for user in  db.query('opratenumbers',{"tel":""},{"_id":tuple(userIdList)})}
    # print userList
    HTML = render_template('distribution/media/list.html',
                           query=query, so=so, title=u'媒体号', Mine=Mine,userList=userList)
    return HTML

@mod.route('/edit', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 3, depict=u'编辑')
def opera_edit():
    Mine = request.Mine()
    if request.method == 'GET':
        id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
        db = SequoiaDB()
        # 3. 查询指定id的数据
        Query = None
        # 3.1 定义查询需要的变量及默认设置
        select = {
            'openid':'',
            'type':'',
            'from_type':'',
            'total_fans':'',
            'total_issue':'',
            'access_token':''
        }
        where = {"_id": (id,)}  # 只有状态为正常的才可以编辑
        for q in db.query('medianumbers', select, where, {}, limit=1):
            Query = q
            break
        if Query is None: return u'您要执行的操作被拦截啦！'
        _brief = u'修改账号 '
        print(Query)
        if Query.type == '1':
            douyin = douyinApi()
            res_fans = douyin.DouyinGetFans(Query.openid, Query.access_token, '15')
            res_like = douyin.DouyinGetUserLike(Query.openid, Query.access_token, '15')
            res_item = douyin.DouyinGetItem(Query.openid, Query.access_token, '15')
            newFans = []
            totalFans = []
            date = []
            new_issue = []
            new_play = []
            total_issue = []
            total_like=[]
            for i in res_fans['data']['result_list']:
                newFans.append(i['new_fans'])
                totalFans.append(i['total_fans'])
                date.append(i['date'])
            for i in res_item['data']['result_list']:
                new_issue.append(i['new_issue'])
                new_play.append(i['new_play'])
                total_issue.append(i['total_issue'])
            for i in res_like['data']['result_list']:
                total_like.append(i['new_like'])
            data = [
                {'name': '每日新粉丝数', 'data': newFans, 'type': 'line'},
                {'name': '每日总粉丝数', 'data': totalFans, 'type': 'line'},
                {'name': '每日新增内容数', 'data': new_issue, 'type': 'line'},
                {'name': '每日新增播放量', 'data': new_play, 'type': 'bar'},
                {'name': '每日内容总数', 'data': total_issue, 'type': 'bar'},
                {'name': '每日点赞总数', 'data': total_like, 'type': 'line'},
            ]
        elif Query.type == '2':
            data=[]
            date=[]
        HTML = render_template('distribution/media/edit.html',title=u'运营账号修改', query=Query,Mine=Mine,data=data,date=date)
        return HTML
    if request.method == 'POST':
        db = SequoiaDB()
        data = {}
        data['tel'] = request.form['tel']
        data['id'] = request.form['id']
        data['password'] = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
        print(data)
        Query = None
        # 3.1 定义查询需要的变量及默认设置
        select = {"tel": "", "addtime": "", "updtime": ""}
        where = {"_id": (data['id'],)}
        for q in db.query('opratenumbers', select, where, {}, limit=1):
            Query = q
            break
        if Query is None: return u'您要执行的操作被拦截啦！'
        Query.update(data, request, event_desc=(1000, u'修改账号[%s]' % Query.tel))

        return redirect(url_for('%s.opera_list' % BLUENAME))
@mod.route('/delete', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 2, depict=u'删除')
def opera_delete():
    Mine = request.Mine()
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    Query = None
    db = SequoiaDB()
    select = {"openid":""}
    where = {"_id": (id,)}

    for q in db.query('medianumbers', select, where, {}, limit=1):
        Query = q
        break
    if Query is None: return u'您要执行的操作被拦截啦！'
    _brief = u'彻底删除%s账号记录'

    remark = '删除媒体号'
    if remark == u'': return u'请确认删除的说明！'
    # 4.1 判断当前登录的用户是否有权限删除本数据

    # 4.2 删除所有下级关联的数据记录（逻辑/物理）

    # 4.3 执行删除（逻辑/物理）
    operater = '%s' % Mine
    desc ='媒体号删除'
    Query.remove(request, event_desc=(999, desc))
    return redirect(url_for('%s.opera_list' % BLUENAME))
