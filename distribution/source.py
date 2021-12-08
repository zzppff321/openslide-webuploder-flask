#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import time
import hashlib
from bson import ObjectId

BLUENAME = 'distribution_source'+'GUI' #Graphical User Interface
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

appid = 20300
_var = locals()

@mod.route('', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+0, depict=u'素材/任务列表', menu=10, remark=u'素材/任务列表')
def opera_list():
    Mine = request.Mine()
    db = SequoiaDB()
    if not db.hascl('source'):
        db.create('source')
    select = {
        "id":"",
        "pic_path": "",
        "video_path": "",
        "play": "",
        "heart": "",
        "share": "",
        "download": "",
        "comment": "",
        "addtime": "",
        "updtime": "",
        "title":"",
        'is_settime':'',
        'settime':'',
        'media_list':'',

    }
    # 3.2 组合查询条件
    so = {u'title': u''}
    # 2.3 获取筛选条件选项的值
    for k, v in so.items():
        _var[k] = so[k] = request.args.get(k, v)
    where = {}
    print(title)
    if not title == u'':
        where['title'] =  {"$regex": '%s' % title}
    if request.args.get('is_settime',default='all') != 'all':
        if request.args.get('is_settime') == '1':
            where['is_settime']=request.args.get('is_settime')
        else:
            where['is_settime']={"$ne":'1'}
    # 默认，按添加时间倒序排列，即新用户在前
    orderby = {"addtime": -1}
    query = db.pagebar('source', select, where, orderby, so)
    for i in query.data:
        i.nickname=[]
        for item in i.media_list.split(','):
            if item:
                row=db.query('medianumbers', {'nickname': ''}, {'_id': (item,)},limit=1)
                if row:
                    print row[0].nickname
                    i.nickname.append(row[0].nickname)
                else:
                    i.nickname.append('账户已注销')
    print query.data
    HTML = render_template('distribution/source/list.html',query=query, so=so, title=u'资源列表', Mine=Mine)
    return HTML

@mod.route('/add', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 1, depict=u'添加')
def opera_add():
    Mine = request.Mine()
    if request.method == 'GET':
        HTML = render_template('distribution/source/add.html',title=u'营销账号添加', Mine=Mine)
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
        res = db.insert(request, 'source', data)
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

        for q in db.query('source', select, where, {}, limit=1):
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
        select = {"tel": "", "addtime": "", "updtime": ""}
        where = {"_id": (id,)}  # 只有状态为正常的才可以编辑
        for q in db.query('opratenumbers', select, where, {}, limit=1):
            Query = q
            break
        if Query is None: return u'您要执行的操作被拦截啦！'
        _brief = u'修改账号 {}'.format(Query.tel)
        print(Query)
        HTML = render_template('distribution/source/edit.html',title=u'营销账号修改', query=Query,Mine=Mine)
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