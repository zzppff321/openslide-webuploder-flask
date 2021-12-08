# coding:utf-8
import requests

import urllib3
import urllib
from urllib import quote
from urllib import unquote

urllib3.disable_warnings()
import json

class kuaishouApi():

    appid = 'ks685954522190317917'
    appsecret =  'jaOsSuF-J-iiimPA1eXYlQ'
    baseUrl = 'https://open.kuaishou.com'


    # curl post
    def post(self,url,data={},files={},header={}):
        res = requests.post(url,data,verify=False,files=files,headers=header)
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
    def kuaishouGetAuthUrl(self,token):
        args={
            "app_id":self.appid,
            "response_type":"code",
            "scope":"user_info,user_video_publish,user_video_info,user_video_delete",
            "redirect_uri":quote("http://znffapi.pg024.com/admin/index.html?token="+token+'&type=2#/authorize-single'),
        }
        url=self.joint(self.baseUrl+'/oauth2/connect',args)
        return url

    def kuaishouGetEmpowerUrl(self, userid):
        args = {
            "app_id": self.appid,
            "response_type": "code",
            "scope": "user_info,user_video_publish,user_video_info,user_video_delete",
            "redirect_uri": quote(
                "http://znffapi.pg024.com/distribution/operating/auth?type=2&userid=" + userid),
        }
        url = self.joint(self.baseUrl + '/oauth2/connect', args)
        return url
    # 获取快手开放平台 access token
    def KuaishouGetAccessToken(self,code):
        params={
            "app_id":self.appid,
            "code":code,
            "app_secret":self.appsecret,
            "grant_type":"authorization_code",

        }
        url=self.baseUrl+'/oauth2/access_token'
        res=self.post(url,params)
        return res
    # 通过access token获取快手用户信息
    def KuaishouGetUserinfo(self,token):
        args = {
            "app_id": self.appid,
            "access_token": token
        }
        url = self.joint(self.baseUrl + '/openapi/user_info', args)
        res=self.get(url)
        return res
    # 上传视频 step 1 开始上传,2 上传文件 ，3 发布视频
    def KuaishouUploadVideo(self,token,video_path,title,pic_path):
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}
        args={
            'access_token':token,
            'app_id':self.appid
        }
        url = self.joint(self.baseUrl+'/openapi/photo/start_upload',args)
        res = self.post(url)
        if res['result'] != 1:
            return res
        args={
            'upload_token':res['upload_token'],
        }
        url  = self.joint('http://'+res['endpoint']+'/api/upload/multipart/',args)
        files = [
            ('file', ('123.mp4', open(video_path, 'rb'), 'application/octet-stream')),
        ]
        res2= self.post(url, {}, files,header)
        print res2
        if res2['result'] != 1:
            return res2
        args={
            'access_token':token,
            'app_id':self.appid,
            'upload_token':res['upload_token'],
        }
        url=self.joint(self.baseUrl+'/openapi/photo/publish',args)
        params={
            'caption':title,
        }
        files = [
            ('cover', ('', open(pic_path, 'rb'), 'application/octet-stream')),
        ]
        return self.post(url,params,files,header)
    # 获取抖音视频列表
    def KuaishouGetVideoList(self,token,page='',pageSize='200'):
        args={
            'access_token':token,
            'cursor':page,
            'count':pageSize,
            'app_id':self.appid,

        }
        return self.get(self.baseUrl+'/openapi/photo/list',args)




