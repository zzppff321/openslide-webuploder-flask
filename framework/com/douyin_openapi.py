# coding:utf-8
import requests

import urllib3
import urllib
from urllib import quote
from urllib import unquote

urllib3.disable_warnings()
import json

class douyinApi():

    DouyinClientKey='awnnzffqw4w7igra'
    DouyinClientSecret='e010a2beacea959216814888eb357318'
    DouyinBaseUrl='https://open.douyin.com'

    # curl post
    def post(self,url,data={},files={}):
        res = requests.post(url,data,verify=False,files=files)
        return res.json()
    # 拼接 curl get 地址
    def joint(self,url,params):
        args = []
        for k in params:
            args.append(k + '=' + params[k])
        if args:
            url += '?' + '&'.join(args)
        return url
    # curl get
    def get(self,url,data={}):
        requestUrl=self.joint(url,data)
        res=requests.get(requestUrl,verify=False)
        return res.json()
    # 生成授权码页面url
    def DouyinGetAuthUrl(self,token):
        args={
            "client_key":self.DouyinClientKey,
            "response_type":"code",
            "scope":"video.create,user_info,video.list,data.external.item,data.external.user,item.comment",
            #http://znffapi.pg024.com/?code=6a52c6c3e0107556iSixfrga16PM8AccDehn&state=&token=d7d14fa0a3829fda73029c0bf121ad86&type=1#/login?redirect=%2Forder
            "redirect_uri":quote("http://znffapi.pg024.com/admin/index.html?token="+token+'&type=1#/authorize-single'),
        }
        url=self.joint(self.DouyinBaseUrl+'/platform/oauth/connect/',args)
        return url

    # 生成平台授权码页面url
    def DouyinGetEmpowerUrl(self, userid):
        args = {
            "client_key": self.DouyinClientKey,
            "response_type": "code",
            "scope": "video.create,user_info,video.list,data.external.item,data.external.user,item.comment",
            # http://znffapi.pg024.com/?code=6a52c6c3e0107556iSixfrga16PM8AccDehn&state=&token=d7d14fa0a3829fda73029c0bf121ad86&type=1#/login?redirect=%2Forder
            "redirect_uri": quote(
                "http://znffapi.pg024.com/distribution/operating/auth?type=1&userid="+userid),
        }
        url = self.joint(self.DouyinBaseUrl + '/platform/oauth/connect/', args)
        return url

    # 获取抖音开放平台 access token
    def DouyinGetAccessToken(self,code):
        params={
            "client_secret":self.DouyinClientSecret,
            "code":code,
            "grant_type":"authorization_code",
            "client_key":self.DouyinClientKey

        }
        url=self.DouyinBaseUrl+'/oauth/access_token/'
        res=self.post(url,params)
        return res
    # 通过access token获取抖音用户信息
    def DouyinGetUserinfo(self,openid,token):
        args = {
            "open_id": openid,
            "access_token": token
        }
        url = self.joint(self.DouyinBaseUrl + '/oauth/userinfo/', args)
        res=self.get(url)
        return res

    #上传视频文件
    def DouyinUploadVideo(self,openid,token,video_path):
        args={
            "open_id":openid,
            "access_token":token
        }
        url=self.joint(self.DouyinBaseUrl+'/video/upload',args)
        files=[
            ('video', ('123.mp4', open(video_path, 'rb'), 'application/octet-stream')),
        ]
        return self.post(url,{},files)
    # 创建视频
    def DouyinCreateVideo(self,openid,token,video_id,title=''):
        args = {
            "open_id": openid,
            "access_token": token
        }
        data={
            "video_id":video_id,
            "text":title
        }
        url = self.joint(self.DouyinBaseUrl + '/video/create', args)
        return self.post(url,json.dumps(data))

    # 获取抖音视频列表
    def DouyinGetVideoList(self,openid,token,page,pageSize):
        args={
            'open_id':openid,
            'access_token':token,
            'cursor':page,
            'count':pageSize
        }
        return self.get(self.DouyinBaseUrl+'/video/list/',args)

    # 获取粉丝数据
    def DouyinGetFansList(self,openid,token):
        args={
            'open_id':openid,
            'access_token':token,
            'count':10
        }
        return self.get(self.DouyinBaseUrl+'/fans/list/',args)
    # 获取关注数量
    def DouyinGetfollowingList(self,openid,token):
        args = {
            'open_id': openid,
            'access_token': token,
            'count': 10
        }
        return self.get(self.DouyinBaseUrl + '/following/list/', args)
    # 获取视频基础数据
    def DouyinGetItemBase(self,openid,token,itemid):
        args={
            'open_id':openid,
            'access_token':token,
            'item_id':itemid
        }
        return self.get(self.DouyinBaseUrl+'/data/external/item/base/?'+urllib.urlencode(args))
    # 获取用户粉丝增长数据
    def DouyinGetFans(self,openid,token,date_type):
        args={
            'open_id': openid,
            'access_token': token,
            'date_type':date_type
        }
        return self.get(self.DouyinBaseUrl + '/data/external/user/fans/',args)
    # 获取用户全部视频增长数据
    def DouyinGetItem(self,openid,token,date_type):
        args={
            'open_id': openid,
            'access_token': token,
            'date_type': date_type
        }
        return self.get(self.DouyinBaseUrl + '/data/external/user/item/',args)
    # 视频点赞趋势
    def DouyinGetItemLike(self,openid,token,date_type,itemid):
        args={
            'open_id': openid,
            'access_token': token,
            'date_type': date_type,
            'item_id':itemid
        }
        return self.get(self.DouyinBaseUrl + '/data/external/item/like/?'+urllib.urlencode(args))
        # 视频点赞趋势

    def DouyinGetUserLike(self, openid, token, date_type):
        args = {
            'open_id': openid,
            'access_token': token,
            'date_type': date_type,
        }
        return self.get(self.DouyinBaseUrl + '/data/external/user/like/?' + urllib.urlencode(args))
    # 视频评论数据趋势
    def DouyinGetItemComment(self,openid,token,date_type,itemid):
        args={
            'open_id': openid,
            'access_token': token,
            'date_type': date_type,
            'item_id':itemid
        }
        return self.get(self.DouyinBaseUrl + '/data/external/item/comment/?'+urllib.urlencode(args))

    # 视频播放趋势
    def DouyinGetItemPlay(self, openid, token, date_type, itemid):
        args = {
            'open_id': openid,
            'access_token': token,
            'date_type': date_type,
            'item_id': itemid
        }
        return self.get(self.DouyinBaseUrl + '/data/external/item/play/?' + urllib.urlencode(args))
    # 视频分享趋势
    def DouyinGetItemShare(self, openid, token, date_type, itemid):
        args = {
            'open_id': openid,
            'access_token': token,
            'date_type': date_type,
            'item_id': itemid
        }
        return self.get(self.DouyinBaseUrl + '/data/external/item/share/?' + urllib.urlencode(args))
    # 评论管理
    def DouyinGetItemCommentList(self, openid, token, itemid,page,pageSize):
        args = {
            'open_id': openid,
            'count':pageSize,
            'cursor':page,
            'access_token': token,
            'item_id': itemid
        }
        return self.get(self.DouyinBaseUrl + '/item/comment/list/?'+urllib.urlencode(args))



