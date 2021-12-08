#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import time
import hashlib
import time
from bson import ObjectId
from com.distribution_api import distributionApi
from com.douyin_openapi import douyinApi
from com.kuaishou_openapi import kuaishouApi
from com.filter import dateformat

BLUENAME = 'distribution_api_platform'
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


appid = 20310
_var = locals()

# 获取各大平台扫码授权链接
@mod.route('/authUrlList',methods=['get'])
def platformList():
    userinfo=distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error',{},-2)
    list= {
        "douyin":douyinApi().DouyinGetAuthUrl(request.args['token']),
        "kuaishou": kuaishouApi().kuaishouGetAuthUrl(request.args['token']),
    }
    return distributionApi().success(list)
# 用抖音授权码换accesstoken


@mod.route('/douyinGetCode',methods=['get'])
def douyinGetCode():
    base = distributionApi()
    userinfo = base.auth()
    if userinfo == False:
        return base.error('token error',{},-2)
    code = request.args.get('code',type=str,default='')
    if code == '':
        return base.error('授权码不能为空')
    type = request.args.get('type', type=str, default='0')
    if type == '1' :
        douyin = douyinApi()
        res=douyin.DouyinGetAccessToken(code)
        if(res['message']=='error'):
            return base.error(res['data']['description'],res['data'])
        douyinUserInfo=douyin.DouyinGetUserinfo(res['data']['open_id'],res['data']['access_token'])
        if(douyinUserInfo['data']['error_code']!=0):
            return base.error('获取抖音用户信息失败',douyinUserInfo)
        cols = {
            "openid":res['data']['open_id'],
            "type":type,
            "from_type":"2",
            "access_token":res['data']['access_token'],
            "refresh_token":res['data']['refresh_token'],
            "parent_id":userinfo.id,
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
            return base.error(res['error_msg'])
        kuaishouUserInfo = kuaishou.KuaishouGetUserinfo(res['access_token'])
        if (kuaishouUserInfo['result'] != 1):
            return base.error('获取快手用户信息失败', kuaishouUserInfo)
        cols = {
            "openid": res['open_id'],
            "type": type,
            "from_type": "2",
            "access_token": res['access_token'],
            "refresh_token": res['refresh_token'],
            "parent_id": userinfo.id,
            "avatar": kuaishouUserInfo['user_info']['head'],
            "nickname": kuaishouUserInfo['user_info']['name'],
            'city': kuaishouUserInfo['user_info']['city'],
            'province': '',
            'country': '',
        }

    base.updateCurrentInfo(cols)
    return base.success(cols, '授权成功')

# 平台账号列表
@mod.route('/mediaList',methods=['get'])
def mediaList():
    userinfo=distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error',{},-2)
    db = SequoiaDB()
    where={'parent_id':userinfo.id}
    type = request.args.get('type',type=str,default='0')
    if type != '0':
        where["type"]=type
    orderby={"addtime":-1}
    select={'oid':'','avatar':'','nickname':'','type':'','province':'','city':'','country':'','openid':''}
    query =db.query('medianumbers',select,where,orderby)
    list=[]
    for i in query:
        list.append({
            'avatar':i.avatar,
            'nickname': i.nickname,
            'type': i.type,
            'province': i.province,
            'city': i.city,
            'country': i.country,
            'openid':i.openid,
            'id':i.id
        })
    return distributionApi().success({"list":list})

# 任务列表
@mod.route('/publishList',methods=['get'])
def publishList():
    userinfo = distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error',{},-2)
    db = SequoiaDB()
    where = {
        'userid': userinfo.id,
        'openid':request.args.get('openid',type=str,default='')
    }
    video_status = request.args.get('video_status', type=int, default=0)
    if video_status != 0:
        where['video_status'] = video_status
    # publishType = request.args.get('publishType', type=int, default=0)
    #
    # if publishType ==2:
    #     where['error_code']=''
    # elif publishType ==3:
    #     where['error_code']={ "$ne": '' }
    where['platform'] = {"$ne": "1"}
    page = request.args.get('page', type=int, default=1)
    pageSize = request.args.get('pageSize', type=int, default=10)
    orderby = {"addtime": -1}
    select = {
        'userid':'',
        'openid':'',
        'type':'',
        'addtime':'',
        'source_id':'',
        'video_id':'',
        'err_code':'',
        'description':'',
        'title':'',
        'video_status':''
    }
    query = db.pagebar('publishsource', select, where, orderby,{},[pageSize,page])
    list = []
    for q in query.data:
        list.append({
            # 'userid':q.userid,
            # 'openid':q.openid,
            'type':q.type,
            'addtime':q.addtime.strftime('%Y-%m-%d %H:%M:%S'),
            'err_code':q.err_code,
            'description':q.description,
            'title':q.title,
            'id':q.id,
            'video_status': q.video_status


        })
    return distributionApi().success({"list":list,"count":query.size})

# 删除任务
@mod.route('/publishDel', methods=['get'])
def publishDel():
    Mine = request.Mine()
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    Query = None
    db = SequoiaDB()
    select = {}
    where = {"_id": (id,)}

    for q in db.query('publishsource', select, where, {}, limit=1):
        Query = q
        break
    if Query is None: return distributionApi().error('数据不存在')
    desc='误差数据删除'
    Query.remove(request, event_desc=(999, desc))
    return distributionApi().success({},'删除成功')

# 平台视频列表

@mod.route('/videoList', methods=['get'])
def videoList():
    userinfo = distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error', {}, -2)
    openid=request.args.get('openid',type=str,default='')
    if openid == '':
        return distributionApi().error('openid 不能为空')
    page=request.args.get('cursor',type=str,default='0')
    pageSize = request.args.get('pageSize', type=str, default='10')
    last_cursor= request.args.get('cursor_curr',type=str,default='')
    db=SequoiaDB()
    where={
        'openid':openid,
        'parent_id':userinfo.id
    }
    select={"openid":'','access_token':'','type':''}
    query=db.query('medianumbers',select,where,{},limit=1)
    if len(query)== 0:
        return distributionApi().error('账号不存在')
    row=query[0]
    video_status = request.args.get('video_status', type=int, default=0)
    if video_status!=0:
        select={
            'is_reviewed':'',
            'video_status':'',
            'title':'',
            'cover':'',
            'share_url':'',
            'is_top':'',
            'create_time':'',
            'item_id':'',
            'statistics':''

        }
        where={"openid":openid,"userid":userinfo.id,'video_status':video_status }
        hasLast = False
        if(page!='0'):
            hasLast  = True
        list=[];
        skip= int(page)*int(pageSize)
        query=db.query('publishsource',select,where,{"create_time":-1},limit=pageSize,skip= skip)
        count = db.count('publishsource',where)
        for i in query:
            list.append({
                'is_reviewed':i.is_reviewed,
                'video_status':i.video_status,
                'title':i.title,
                'cover':i.cover,
                'share_url':i.share_url,
                'is_top':i.is_top,
                'create_time':i.create_time,
                'item_id':i.item_id,
                'statistics':i.statistics

            })
        data={
            'list':list,
            'description':'',
            'has_more':True if skip + int(pageSize) < count else False,
            'cursor':int(page)+1,
            'error_code':0,
            'has_last':hasLast
        }
        return distributionApi().success(data)
    else:
        #抖音
        if row.type == '1':
            douyin = douyinApi()
            res=douyin.DouyinGetVideoList(openid,row.access_token,page,pageSize)
            if res['extra']['error_code'] != 0:
                return distributionApi().error(res['extra']['description'])
            else:
                data = res['data']
                video_website='tiktok'
        #快手
        elif row.type == '2':
            kuaishou=kuaishouApi()
            res = kuaishou.KuaishouGetVideoList(row.access_token,page,pageSize)
            if res['result'] != 1:
                if(res['error']=='access_denied'):
                    return distributionApi().error('授权已过期，请重新扫码授权',{},3)
                else:
                    return distributionApi().error(res)
            else:
                if len(res['video_list'])== 0:
                    return distributionApi().success({},'没有更多了')
                list=[]
                for item in res['video_list']:
                    list.append({
                        'statistics':{
                            'forward_count':0,
                            'digg_count':item['like_count'],
                            'play_count':item['view_count'],
                            'comment_count':item['comment_count'],
                            'share_count':0,
                            'download_count':0
                        },
                        'is_reviewed':item['pending'],
                        'video_status':4 if item['pending']==True else 1,
                        'title':item['caption'],
                        'cover':item['cover'],
                        'share_url':item['play_url'],
                        'is_top':False,
                        'create_time':item['create_time']/1000,
                        'item_id':item['photo_id']
                    })
                nextPgae=kuaishou.KuaishouGetVideoList(row.access_token,res['video_list'][-1]['photo_id'],'1')
                data={
                    'list':list,
                    'cursor':res['video_list'][-1]['photo_id'],
                    'has_more':False if len(nextPgae['video_list'])== 0 else True,
                    'error_code':'0'
                }
                video_website = 'kwai'

        #其他
        else:
            return distributionApi().error('尚未接入该平台')
        for i in data['list']:
            cols = {
                'type':row.type,
                'cover': i['cover'],
                'title': i['title'],
                'share_url': i['share_url'],
                'video_status': i['video_status'],
                'create_time': (i['create_time']),
                'is_top': i['is_top'],
                'userid': userinfo.id,
                'openid': openid,
                'statistics':i['statistics'],
                'video_website': video_website,
                'item_id':i['item_id'],
            }
            where={
                'item_id':i['item_id'],
                'userid':userinfo.id
            }
            res = db.query('publishsource',where, where, {}, limit=1)
            if res :
                res[0].update(cols,request,event_desc=(1000, u'数据更新[%s]' % res[0].id))
            else:
                cols['platform']='1'
                db.insert(request, 'publishsource', cols)
        data['has_last']= True if last_cursor != '' else False
        return distributionApi().success(data)

# 平台视频图表详情
@mod.route('/videoDetailChart', methods=['post'])
def videoDetailChart():
    userinfo = distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error', {}, -2)
    openid=request.form.get('openid',type=str,default='')
    itemid = request.form.get('item_id', type=str, default='')
    datatype = request.form.get('datatype', type=str, default='7')
    res=distributionApi().checkRequestParams(request,['openid','item_id'])
    if res !=False:
        return distributionApi().error(res+'不能为空')
    where={
        'openid':openid,
        'parent_id':userinfo.id
    }
    select={"openid":'','access_token':'','type':''}
    db = SequoiaDB()
    query=db.query('medianumbers',select,where,{},limit=1)
    if len(query)== 0:
        return distributionApi().error('账号不存在')
    row=query[0]
    #抖音
    if row.type == '1':
        douyin = douyinApi()
        res_like=douyin.DouyinGetItemLike(openid,row.access_token,datatype,itemid)
        res_comment = douyin.DouyinGetItemComment(openid, row.access_token, datatype,itemid)
        res_play = douyin.DouyinGetItemPlay(openid, row.access_token, datatype,itemid)
        res_share = douyin.DouyinGetItemShare(openid, row.access_token, datatype,itemid)
        if res_like['extra']['error_code'] != 0:
            return distributionApi().error(res_like['extra']['description'])
        else:
            like=[]
            comment=[]
            date=[]
            play=[]
            share=[]
            for i in res_like['data']['result_list']:
                like.append(i['like'])
                date.append(i['date'])
            for i in res_comment['data']['result_list']:
                comment.append(i['comment'])
            for i in res_play['data']['result_list']:
                play.append(i['play'])
            for i in res_share['data']['result_list']:
                share.append(i['share'])
            data=[
                {'name':'点赞数','data':like,'type':'line'},
                {'name': '播放数', 'data': play,'type':'line'},
                {'name': '评论数', 'data': comment,'type':'line'},
                {'name': '分享数', 'data': share,'type':'line'},
            ]
            fansChart=distributionApi().getChart(date,data)
            return distributionApi().success({'chart':fansChart})
    else:
        return distributionApi().success({'chart': []})

# 平台视频详情
@mod.route('/videoDetailComment', methods=['post'])
def videoDetailComment():
    userinfo = distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error', {}, -2)
    openid=request.form.get('openid',type=str,default='')
    itemid = request.form.get('item_id', type=str, default='')
    page = request.form.get('page', type=str, default='0')
    pageSize = request.form.get('pageSize', type=str, default='10')
    res=distributionApi().checkRequestParams(request,['openid','item_id'])
    if res !=False:
        return distributionApi().error(res+'不能为空')
    where={
        'openid':openid,
        'parent_id':userinfo.id
    }
    select={"openid":'','access_token':'','type':''}
    db = SequoiaDB()
    query=db.query('medianumbers',select,where,{},limit=1)
    if len(query)== 0:
        return distributionApi().error('账号不存在')
    row=query[0]
    #抖音
    if row.type == '1':
        douyin = douyinApi()
        res=douyin.DouyinGetItemBase(openid,row.access_token,itemid)
        res_comment = douyin.DouyinGetItemCommentList(openid, row.access_token, itemid , page , pageSize)
        if res['extra']['error_code'] != 0:
            return distributionApi().error(res['extra']['description'])
        else:
            data={
                'baseInfo':res['data'],
                'commentInfo':res_comment['data']
            }
            return distributionApi().success(data)
    #快手
    elif row.type == '2':
        kuaishou=kuaishouApi()
        res = kuaishou.KuaishouGetVideoList(row.access_token,page,pageSize)
        if res['result'] != 1:
            return distributionApi().error(res)
        else:
            list=[]
            for item in res['video_list']:
                list.append({
                    'statistics':{
                        'forward_count':0,
                        'digg_count':item['like_count'],
                        'play_count':item['view_count'],
                        'comment_count':item['comment_count'],
                        'share_count':0,
                        'download_count':0
                    },
                    'is_reviewed':item['pending'],
                    'video_status':item['pending'],
                    'title':item['caption'],
                    'cover':item['cover'],
                    'share_url':item['play_url'],
                    'is_top':False,
                    'create_time':item['create_time'],
                    'item_id':item['photo_id']
                })
            return distributionApi().success({'list':list})
    #其他
    else:
        return distributionApi().error('尚未接入该平台')

# 授权后首页echart+最近视频
@mod.route('/index', methods=['get'])
def index():
    userinfo = distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error', {}, -2)
    openid=request.args.get('openid',type=str,default='')
    res=distributionApi().checkRequestParams(request,['openid'])
    if res !=False:
        return distributionApi().error(res+'不能为空')
    where={
        'openid':openid,
        'parent_id':userinfo.id
    }
    select={"openid":'','access_token':'','type':''}
    db = SequoiaDB()
    query=db.query('medianumbers',select,where,{},limit=1)
    if len(query)== 0:
        return distributionApi().error('账号不存在')
    row=query[0]
    #抖音
    if row.type == '1':
        douyin = douyinApi()
        res_fans=douyin.DouyinGetFans(openid,row.access_token,'30')
        res_item = douyin.DouyinGetItem(openid, row.access_token, '30')
        if res_fans['extra']['error_code'] != 0:
            return distributionApi().error(res_fans['extra']['description'])
        if res_item['extra']['error_code'] != 0:
            return distributionApi().error(res_item['extra']['description'])
        else:
            newFans=[]
            totalFans=[]
            date=[]
            new_issue=[]
            new_play=[]
            total_issue=[]
            for i in res_fans['data']['result_list']:
                newFans.append(i['new_fans'])
                totalFans.append(i['total_fans'])
                date.append(i['date'])
            for i in res_item['data']['result_list']:
                new_issue.append(i['new_issue'])
                new_play.append(i['new_play'])
                total_issue.append(i['total_issue'])
            data = [
                {'name': '每日新粉丝数', 'data': newFans,'type':'line'},
                {'name': '每日总粉丝数', 'data': totalFans,'type':'line'},
                {'name': '每日新增内容数', 'data': new_issue,'type':'line'},
                {'name': '每日新增播放量', 'data': new_play,'type':'bar'},
                {'name': '每日内容总数', 'data': total_issue,'type':'bar'},
            ]
            fansChart = distributionApi().getChart(date, data)
            row.update({
                "total_fans":res_fans['data']['result_list'][-1]['total_fans'],
                "total_issue":res_item['data']['result_list'][-1]['total_issue'],
            },request)
            return distributionApi().success({
                'chart':fansChart,
                'totalFans':res_fans['data']['result_list'][-1]['total_fans'],
                'total_issue': res_item['data']['result_list'][-1]['total_issue'],
            })
    elif row.type =='2':
        row.update({
            "total_fans": "暂不支持",
            "total_issue": "暂不支持",
        },request)
        return distributionApi().success({
            'chart': [],
            'totalFans': '暂不支持',
            'total_issue': '暂不支持',
        })
    #其他
    else:
        return distributionApi().error('尚未接入该平台')

@mod.route('/billboard', methods=['get'])
def billboard():
    userinfo = distributionApi().auth()
    if userinfo == False:
        return distributionApi().error('token error', {}, -2)
    openid=request.args.get('openid',type=str,default='')
    if openid == '':
        return distributionApi().error('openid 不能为空')
    page='0'
    pageSize = '20'
    db=SequoiaDB()
    where={
        'openid':openid,
        'parent_id':userinfo.id
    }
    select={"openid":'','access_token':'','type':''}
    query=db.query('medianumbers',select,where,{},limit=1)
    if len(query)== 0:
        return distributionApi().error('账号不存在')
    row=query[0]
    #抖音
    if row.type == '1':
        douyin = douyinApi()
        res=douyin.DouyinGetVideoList(openid,row.access_token,page,pageSize)
        if res['extra']['error_code'] != 0:
            return distributionApi().error(res['extra']['description'])
        else:
            list = res['data']['list']


    #快手
    elif row.type == '2':
        kuaishou=kuaishouApi()
        res = kuaishou.KuaishouGetVideoList(row.access_token,'','4')
        if res['result'] != 1:
            return distributionApi().error(res)
        else:
            list=[]
            for item in res['video_list']:
                list.append({
                    'statistics':{
                        'forward_count':0,
                        'digg_count':item['like_count'],
                        'play_count':item['view_count'],
                        'comment_count':item['comment_count'],
                        'share_count':0,
                        'download_count':0
                    },
                    'is_reviewed':item['pending'],
                    'video_status':item['pending'],
                    'title':item['caption'],
                    'cover':item['cover'],
                    'share_url':item['play_url'],
                    'is_top':False,
                    'create_time':item['create_time'],
                    'item_id':item['photo_id']
                })
    #其他
    else:
        return distributionApi().error('尚未接入该平台')

    digg_count = sorted(list, key = lambda k: k['statistics']['digg_count'])
    digg_count.reverse()
    comment_count = sorted(list, key=lambda k: k['statistics']['comment_count'])
    comment_count.reverse()
    play_count = sorted(list, key=lambda k: k['statistics']['play_count'])
    play_count.reverse()
    return distributionApi().success({
        'comment':comment_count[:4],
        'play':play_count[:4],
        'digg':play_count[:4]
    })

