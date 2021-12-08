#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import time
import hashlib,json
from com.douyin_openapi import douyinApi
from com.distribution_api import distributionApi
from com.kuaishou_openapi import kuaishouApi
from bson import ObjectId

BLUENAME = 'distribution_publishsource'+'GUI' #Graphical User Interface
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

appid = 20400
_var = locals()

@mod.route('', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+0, depict=u'内容列表', menu=10, remark=u'内容列表')
def opera_list():
    Mine = request.Mine()
    db = SequoiaDB()
    if not db.hascl('publishsource'):
        db.create('publishsource')
    select = {
        "id":"",
        "cover": "",
        "statistics": "",
        "userid":'',
        "openid":"",
        "item_id":"",
        "title":"",
        "platform":"",
        "video_status":"",
        'create_time':''

    }
    # 3.2 组合查询条件
    so = {u'title': u''}
    # 2.3 获取筛选条件选项的值
    for k, v in so.items():
        _var[k] = so[k] = request.args.get(k, v)
    where = {}
    if request.args.get('userid'):
        where['userid']=request.args.get('userid')
    if request.args.get('openid'):
        where['openid'] = request.args.get('openid')
    if request.args.get('title'):
        where['title'] =  {"$regex": '%s' % request.args.get('title')}
    if request.args.get('video_status',default='0') != '0':
        where['video_status'] = int( request.args.get('video_status'))
    if request.args.get('platform',default='all') != 'all':
        where['platform']=request.args.get('platform')
    # 默认，按添加时间倒序排列，即新用户在前
    orderby = {"addtime": -1}
    query = db.pagebar('publishsource', select, where, orderby, so,[20,request.args.get('p',default=1,type= int)])
    for i in query.data:
        if i.create_time:
            i.create_time =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(i.create_time)))
        else:
            i.create_time = "平台未提供"
    HTML = render_template('distribution/publishsource/list.html',
                           query=query, so=so, title=u'资源列表', Mine=Mine)
    return HTML

@mod.route('/add', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 1, depict=u'添加')
def opera_add():
    Mine = request.Mine()
    if request.method == 'GET':
        HTML = render_template('distribution/publishsource/add.html',title=u'营销账号添加', Mine=Mine)
        return HTML
    if request.method == 'POST':
        db = SequoiaDB()
        data = {}
        data['tel'] = request.form['tel']
        data['password'] = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
        where = {}
        select = {"tel": "", "addtime": "", "updtime": ""}
        where['tel'] = data['tel']
        Query = None
        for q in db.query('opratenumbers', select, where, {}, limit=1):
            Query = q
            break
        print(Query)
        if Query is not None: return u'当前账号已被使用！'
        print(data)
        res = db.insert(request, 'publishsource', data)
        print(res)
        return redirect(url_for('%s.opera_list' % BLUENAME))


@mod.route('/delete', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 2, depict=u'删除')
def opera_delete():
    Mine = request.Mine()
    # 2. 获取被编辑对象的id
    ids = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    Query = None
    db = SequoiaDB()
    select = {"title": "", "addtime": "", "updtime": "",}
    for id in ids.split(','):
        where = {"_id": (id,)}

        for q in db.query('publishsource', select, where, {}, limit=1):
            Query = q
            break
        if Query is None: return u'您要执行的操作被拦截啦！'
        _brief = u'彻底删除%s账号记录【%s】' % (Query.title,Query.id)

        remark = '删除素材'
        if remark == u'': return u'请确认删除的说明！'
        # 4.1 判断当前登录的用户是否有权限删除本数据

        # 4.2 删除所有下级关联的数据记录（逻辑/物理）

        # 4.3 执行删除（逻辑/物理）
        operater = '%s' % Mine
        desc = u'{}删除由{}添加的账号记录，删除说明：{}'.format(operater, Query.title, remark)
        Query.remove(request, event_desc=(999, desc))
    return redirect(url_for('%s.opera_list' % BLUENAME))

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
            'item_id':'',
            'openid':'',
            'statistics':''
        }
        where = {"_id": (id,)}  # 只有状态为正常的才可以编辑
        for q in db.query('publishsource', select, where, {}, limit=1):
            Query = q
            break
        if Query is None: return u'您要执行的操作被拦截啦！'
        _brief = u'查看账号'
        datatype = 30
        query=db.query('medianumbers', {"access_token":"","type":""}, {'openid':Query.openid}, {}, limit=1)
        q = query[0]

        # 抖音
        if q.type == '1':
            douyin = douyinApi()
            res_like = douyin.DouyinGetItemLike(Query.openid, q.access_token, datatype, Query.item_id)
            res_comment = douyin.DouyinGetItemComment(Query.openid, q.access_token, datatype, Query.item_id)
            res_play = douyin.DouyinGetItemPlay(Query.openid, q.access_token, datatype, Query.item_id)
            res_share = douyin.DouyinGetItemShare(Query.openid, q.access_token, datatype, Query.item_id)
            if res_like['extra']['error_code'] != 0:
                return distributionApi().error(res_like['extra']['description'])
            else:
                like = []
                comment = []
                date = []
                play = []
                share = []
                for i in res_like['data']['result_list']:
                    like.append(i['like'])
                    date.append(i['date'])
                for i in res_comment['data']['result_list']:
                    comment.append(i['comment'])
                for i in res_play['data']['result_list']:
                    play.append(i['play'])
                for i in res_share['data']['result_list']:
                    share.append(i['share'])
                data = [
                    {'name': '点赞数', 'data': like, 'type': 'line'},
                    {'name': '播放数', 'data': play, 'type': 'line'},
                    {'name': '评论数', 'data': comment, 'type': 'line'},
                    {'name': '分享数', 'data': share, 'type': 'line'},
                ]
        else:
            date=[]
            data=[]



        HTML = render_template('distribution/publishsource/edit.html',title=u'营销账号修改', query=Query,Mine=Mine,date=date,data=data)
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