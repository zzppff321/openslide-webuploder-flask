#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import time
import hashlib
from com.douyin_openapi import douyinApi
from com.kuaishou_openapi import kuaishouApi
from com.distribution_api import distributionApi
from bson import ObjectId

BLUENAME = 'distribution_operating'+'GUI' #Graphical User Interface
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

appid = 20100
_var = locals()

@mod.route('', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+0, depict=u'运营账号列表', menu=10, remark=u'运营账号列表')
def opera_list():
    Mine = request.Mine()
    db = SequoiaDB()
    if not db.hascl('opratenumbers'):
        db.create('opratenumbers')
    select = {"id":"","tel": "", "addtime": "", "updtime": "","token":""}
    # 3.2 组合查询条件
    so = {u'tel': u''}
    # 2.3 获取筛选条件选项的值
    for k, v in so.items():
        _var[k] = so[k] = request.args.get(k, v)
    where = {}
    if not tel == u'':
        where['tel'] =  {"$regex": '%s' % tel}
        mediaList=db.query('medianumbers',{"parent_id":""},{"nickname":{"$regex": '%s' % tel}})
        userList=[]
        for i in mediaList:
            userList.append(i.parent_id)
        if userList :
            # print userList
            where['_id'] = (userList[0],)
    # 默认，按添加时间倒序排列，即新用户在前
    orderby = {"addtime": -1}
    query = db.pagebar('opratenumbers', select, where, orderby, so)
    for item in query.data:
        item.mediaCount = db.count('medianumbers',{"parent_id":str(item.oid)})
        item.sourceCount = db.count('publishsource', {"userid": str(item.oid)})
        item.forbiddenCount = db.count('publishsource', {"userid": str(item.oid),"video_status":2})
    HTML = render_template('distribution/operating/list.html',
                           query=query, so=so, title=u'运营账号', Mine=Mine)
    return HTML

@mod.route('/add', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 1, depict=u'添加')
def opera_add():
    Mine = request.Mine()
    if request.method == 'GET':
        HTML = render_template('distribution/operating/add.html',title=u'运营账号添加', Mine=Mine)
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
        res = db.insert(request, 'opratenumbers', data)
        print(res)
        return redirect(url_for('%s.opera_list' % BLUENAME))


@mod.route('/delete', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 2, depict=u'删除')
def opera_delete():
    Mine = request.Mine()
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    Query = None
    db = SequoiaDB()
    select = {"tel": "", "addtime": "", "updtime": "",}
    where = {"_id": (id,)}

    for q in db.query('opratenumbers', select, where, {}, limit=1):
        Query = q
        break
    if Query is None: return u'您要执行的操作被拦截啦！'
    _brief = u'彻底删除%s账号记录【%s】' % (Query.tel,Query.id)

    remark = '删除运营账号'
    if remark == u'': return u'请确认删除的说明！'
    # 4.1 判断当前登录的用户是否有权限删除本数据

    # 4.2 删除所有下级关联的数据记录（逻辑/物理）

    # 4.3 执行删除（逻辑/物理）
    operater = '%s' % Mine
    desc = u'{}删除由{}添加的账号记录，删除说明：{}'.format(operater, Query.tel, remark)
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
        select = {"tel":""}
        where = {"_id": (id,)}  # 只有状态为正常的才可以编辑
        for q in db.query('opratenumbers', select, where, {}, limit=1):
            Query = q
            break
        if Query is None: return u'您要执行的操作被拦截啦！'
        _brief = u'修改账号 {}'.format(Query.tel)
        print(Query)
        HTML = render_template('distribution/operating/edit.html',title=u'运营账号修改', query=Query,Mine=Mine)
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

@mod.route('/empower',methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 4, depict=u'授权')
def opera_empower():
    Mine = request.Mine()
    userid=request.args.get('id')
    list = {
        "douyin": douyinApi().DouyinGetEmpowerUrl(userid),
        "kuaishou": kuaishouApi().kuaishouGetEmpowerUrl(userid),
    }
    HTML = render_template('distribution/operating/empower.html',list =list)
    return HTML


@mod.route('/auth',methods=['get'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid + 5, depict=u'获取token')
def opera_auth():

    code = request.args.get('code',type=str,default='')
    type = request.args.get('type', type=str, default='0')
    if type == '1' :
        douyin = douyinApi()
        res=douyin.DouyinGetAccessToken(code)
        if(res['message']=='error'):
            return distributionApi().error(res['data']['description'],res['data'])
        douyinUserInfo=douyin.DouyinGetUserinfo(res['data']['open_id'],res['data']['access_token'])
        if(douyinUserInfo['data']['error_code']!=0):
            return distributionApi().error('获取抖音用户信息失败',douyinUserInfo)
        cols = {
            "openid":res['data']['open_id'],
            "type":type,
            "from_type":"1",
            "access_token":res['data']['access_token'],
            "refresh_token":res['data']['refresh_token'],
            "parent_id": request.args.get('userid'),
            "avatar":douyinUserInfo['data']['avatar'],
            "nickname": douyinUserInfo['data']['nickname'],
            "union_id":douyinUserInfo['data']['union_id'],
            'city':douyinUserInfo['data']['city'],
            'province': douyinUserInfo['data']['province'],
            'country': douyinUserInfo['data']['country'],
        }
    else:
        kuaishou = kuaishouApi()
        res = kuaishou.KuaishouGetAccessToken(code)
        if (res['result'] != 1):
            return distributionApi().error(res['error_msg'])
        kuaishouUserInfo = kuaishou.KuaishouGetUserinfo(res['access_token'])
        if (kuaishouUserInfo['result'] != 1):
            return distributionApi().error('获取快手用户信息失败', kuaishouUserInfo)
        cols = {
            "openid": res['open_id'],
            "type": type,
            "from_type": "1",
            "access_token": res['access_token'],
            "refresh_token": res['refresh_token'],
            "parent_id": request.args.get('userid'),
            "avatar": kuaishouUserInfo['user_info']['head'],
            "nickname": kuaishouUserInfo['user_info']['name'],
            'city': kuaishouUserInfo['user_info']['city'],
            'province': '',
            'country': '',
        }

    distributionApi().updateCurrentInfo(cols)
    # return distributionApi().success(cols, '授权成功')
    HTML = render_template('distribution/operating/alert.html', msg='授权成功')
    return HTML