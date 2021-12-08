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

BLUENAME = 'distribution_api_video'
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)
import requests
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
# 视频列表
@mod.route('/list', methods=['GET'])
def list():
    base=distributionApi()
    userinfo=base.auth()
    if userinfo == False:
        return base.error('token error',{},-2)
    data = {
        "id": userinfo.id,
        "tel": userinfo.tel
    }
    page = request.args.get('page', type=int, default=1)
    pageSize = request.args.get('pageSize', type=int, default=10)
    where = {'userid': userinfo.id}
    db=SequoiaDB()
    select={"pic_path":"","title":"","video_path":"","play":"","heart":"","share":"","download":"","comment":"","addtime":"","updatetime":""}
    orderby={"addtime":-1}
    query = db.pagebar('source', select, where, orderby, {},[pageSize,page])
    list=[]
    for q in query.data:
        list.append({
            "pic_path":q.pic_path,
            "title":q.title,
            "video_path":q.video_path,
            'play':q.play,
            'heart': q.heart,
            'share': q.share,
            'download': q.download,
            'comment': q.comment,
            'addtime':dateformat(q.addtime,"%Y-%m-%d %H:%M:%S"),
            # 'updatetime': q.updatetime.datetime('%Y-%m-%d %H:%M:%S'),
            'id':q.id
        })
    return base.success({"list":list,"count":query.size,"userinfo":data})
# 任务发布
@mod.route('/save',methods=['post'])
def save():
    base = distributionApi()
    userinfo = base.auth()
    if userinfo == False:
        return base.error('token error',{},-2)
    # data = {
    #     "id": userinfo.id,
    #     "tel": userinfo.tel
    # }
    pic_path = request.form.get('pic_path',type=str,default='').encode('utf-8')
    video_path = request.form.get('video_path',type=str,default='').encode('utf-8')
    new_pic_path = request.form.get('new_pic_path', type=str, default='').encode('utf-8')
    new_video_path = request.form.get('new_video_path', type=str, default='').encode('utf-8')
    mediaIdList= request.form.get('media_id',type=str,default='').encode('utf-8').split(',')
    distributionApi().checkRequestParams(request,['media_id','new_video_path'])

    db = SequoiaDB()
    for media_id in mediaIdList:
        select = {'openid': '', 'access_token': '', 'type': ''}
        order = {}
        where = {"_id": (media_id,)}
        query = db.query('medianumbers', select, where, order, limit=1)
        if query[0].type=='2' and new_pic_path == '':
            return base.error('上传快手视频，封面图片不能为空')

    if new_pic_path != '':
        pic_path=base.moveUploadFile(new_pic_path,pic_path)
        if pic_path == False:
            return base.error('pic upload error')
    if new_video_path != '':
        video_path=base.moveUploadFile(new_video_path,video_path)
        if video_path == False:
            return base.error('video upload error')

    cols={
        'title':request.form.get('title',type=str,default='').encode('utf-8'),
        'pic_path':pic_path,
        'video_path':video_path,
        'remark':request.form.get('remark',type=str,default='').encode('utf-8'),
        'userid':userinfo.id,
        'media_list':request.form.get('media_id', type=str, default='').encode('utf-8'),
    }
    # print cols
    id = request.form.get('id',type=str,default=None)
    if id is None:
        res=db.insert(request,'source',cols)
        for media_id in mediaIdList:
            response=createVideo(media_id,video_path,res,userinfo.id,cols['title'],pic_path)
            if(response['res'] == False):
                return base.error(response['info'],{},response['rc'])
    else:
        query = None
        for q in db.query("source",{},{"_id":(id,)},limit=1):
            query=q
            break
        if query is None:
            return base.error('数据错误')
        query.update(cols,request)
        res= True
    if res:
        return base.success({},'视频创建成功')
    else:
        return base.error('上传视频失败，请过儿再试')
# 上传视频到抖音并且保存发布任务
def createVideo(media_id,video_path,source_id,userid,title,pic_path=''):
    mediaPath = distributionApi().root_path() + '/media/'
    video_path = mediaPath + video_path
    if pic_path!='':
        pic_path = mediaPath+pic_path
    db=SequoiaDB()
    select={'openid':'','access_token':'','type':''}
    order={}
    where = {"_id": (media_id,)}
    query=db.query('medianumbers',select,where,order,limit=1)
    row=query[0]
    if row.type == '1':
        # 抖音
        douyin = douyinApi()
        error_code = video_id = item_id = ''
        description = '发布成功'
        r1= True
        res = douyin.DouyinUploadVideo(row.openid, row.access_token,video_path)
        if res['extra']['error_code'] !=0:
            error_code =res['extra']['error_code']
            description =res['extra']['description']
            r1=False
            rc =1
        else:
            rc=0
            video_id= res['data']['video']['video_id']
            res = douyin.DouyinCreateVideo(row.openid,row.access_token,video_id,title)
            if res['extra']['error_code'] != 0:
                error_code = res['extra']['error_code']
                description = res['extra']['description']
                r1 = False
            else:
                item_id = res['data']['item_id']
            if not db.hascl('publishsource'):
                db.create('publishsource')
            cols={
                "title":title,
                "userid":userid,
                "openid":row.openid,
                "type":row.type,
                "source_id":source_id,
                "video_id":video_id,
                "error_code":error_code,
                "description":description,
                "item_id":item_id,
                "platform": '0'
            }
            db.insert(request,'publishsource',cols)
        return {"res":r1,"info":description,'rc':rc}
    elif row.type=='2':
        kuaishou = kuaishouApi()
        error_code = video_id = item_id = ''
        description = '发布成功'
        r1 = True
        res = kuaishou.KuaishouUploadVideo(row.access_token, video_path,title,pic_path)
        if res['result'] != 1:
            description = res['error_msg']
            if(res['error_msg']=='ACCESS_DENIED'):
                description='授权过期，请重新扫码授权'
                rc = 3
            else:
                rc = 1
            r1 = False
        else:
            if not db.hascl('publishsource'):
                db.create('publishsource')
            rc=0
            cols = {
                "title": title,
                "userid": userid,
                "openid": row.openid,
                "type": row.type,
                "source_id": source_id,
                "video_id": video_id,
                "error_code": error_code,
                "description": description,
                "item_id": res['video_info']['photo_id'],
                "platform":'0'
            }
            db.insert(request, 'publishsource', cols)
        return {"res": r1, "info": description,"rc":rc}
    else:
        return {"res":False,"info":"平台类型尚未接入，尽请期待",'rc':1}
# 定时任务发布
@mod.route('/saveSettime',methods=['post'])
def saveSettime():
    base = distributionApi()
    userinfo = base.auth()
    if userinfo == False:
        return base.error('token error', {}, -2)
    # data = {
    #     "id": userinfo.id,
    #     "tel": userinfo.tel
    # }
    pic_path = request.form.get('pic_path', type=str, default='').encode('utf-8')
    video_path = request.form.get('video_path', type=str, default='').encode('utf-8')
    new_pic_path = request.form.get('new_pic_path', type=str, default='').encode('utf-8')
    new_video_path = request.form.get('new_video_path', type=str, default='').encode('utf-8')
    settime = request.form.get('settime', type=str, default='').encode('utf-8')
    mediaIdList = request.form.get('media_id', type=str, default='').encode('utf-8').split(',')
    distributionApi().checkRequestParams(request, ['media_id', 'new_video_path','settime'])

    db = SequoiaDB()
    for media_id in mediaIdList:
        select = {'openid': '', 'access_token': '', 'type': ''}
        order = {}
        where = {"_id": (media_id,)}
        query = db.query('medianumbers', select, where, order, limit=1)
        if query[0].type == '2' and new_pic_path == '':
            return base.error('上传快手视频，封面图片不能为空')

    if new_pic_path != '':
        pic_path = base.moveUploadFile(new_pic_path, pic_path)
        if pic_path == False:
            return base.error('pic upload error')
    if new_video_path != '':
        video_path = base.moveUploadFile(new_video_path, video_path)
        if video_path == False:
            return base.error('video upload error')

    cols = {
        'title': request.form.get('title', type=str, default='').encode('utf-8'),
        'pic_path': pic_path,
        'video_path': video_path,
        'remark': request.form.get('remark', type=str, default='').encode('utf-8'),
        'userid': userinfo.id,
        'media_list':request.form.get('media_id', type=str, default='').encode('utf-8'),
        'settime':settime,
        'is_settime':'1',
        'publish_status':'0'
    }
    # print cols
    id = request.form.get('id', type=str, default=None)
    if id is None:
        res = db.insert(request, 'source', cols)
    else:
        query = None
        for q in db.query("source", {}, {"_id": (id,)}, limit=1):
            query = q
            break
        if query is None:
            return base.error('数据错误')
        query.update(cols, request)
        res = True
    if res:
        return base.success({}, '定时任务创建成功')
    else:
        return base.error('任务创建失败，请过会儿再试')



@mod.route('/listSettime', methods=['GET'])
def listSettime():
    base=distributionApi()
    userinfo=base.auth()
    if userinfo == False:
        return base.error('token error',{},-2)
    data = {
        "id": userinfo.id,
        "tel": userinfo.tel
    }
    where={'userid':userinfo.id,'is_settime':'1'}
    page=request.args.get('page',type=int,default=1)
    pageSize = request.args.get('pageSize', type=int, default=10)
    db=SequoiaDB()
    select={'title':'','addtime':'','settime':'','publish_status':''}
    orderby={"addtime":-1}
    query = db.pagebar('source', select, where, orderby, {},[pageSize,page])
    list=[]
    for q in query.data:
        list.append({
            "title":q.title,
            "publish_status": '已发布' if q.publish_status=='1' else '未发布',
            "settime": q.settime,
            'addtime':dateformat(q.addtime,"%Y-%m-%d %H:%M:%S"),
            # 'updatetime': q.updatetime.datetime('%Y-%m-%d %H:%M:%S'),
            'id':q.id
        })
    return base.success({"list":list,"count":query.size,"userinfo":data})


@mod.route('/setTime', methods=['GET'])
def setTime():
    db = SequoiaDB()
    select = {'media_list':'','pic_path':'','video_path':'','userid':'','title':'','settime':''}
    where={'is_settime':'1','publish_status': {"$ne": "1"}}
    query = db.query('source', select, where, {})
    res=[]
    for item in query:
        mediaList=item.media_list.split(',')
        for i in mediaList:
            datetime = item.settime+':00'
            timeArray = time.strptime(datetime, "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            if timeStamp <= time.time():
                # print "res.append(createVideo("+i+","+item.video_path+","+str(item.oid)+","+item.userid+","+item.title,item.pic_path+")"
                res.append(createVideo(i,item.video_path,str(item.oid),item.userid,item.title,item.pic_path))
        item.update({'publish_status':'1'}, request)
    return distributionApi().success(res)