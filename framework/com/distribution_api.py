# coding:utf-8
from com.db import SequoiaDB
from flask import Response,request,current_app
import shutil,os
import json
import requests
import sys

class distributionApi():

    DouyinClientKey='awnnzffqw4w7igra'
    DouyinClientSecret='e010a2beacea959216814888eb357318'
    DouyinBaseUrl='https://open.douyin.com'
    DouyinCode='6a52c6c3e01075569r79SaRJWNoo1l6dS7ch'

    def auth(self):
        db = SequoiaDB()
        orderby={}
        token = request.values.get('token',type=str,default=None)
        if token is None:
            return False
        where={"token":token}
        res = db.query('opratenumbers', {"tel":""}, where, orderby, limit=1)
        if not res :
            return False
        else:
            return res[0]
    # ajax success return
    def success(self,data={},msg='success',rc=0):
        
        return Response(json.dumps({"rc":rc,"msg":msg,"data":data}), mimetype='application/json',headers={"Access-Control-Allow-Origin":'*','Access-Control-Allow-Headers':'*'})
    # ajax error return
    def error(self,msg='error',data={},rc=1):
        return Response(json.dumps({"rc": rc, "msg": msg, "data": data}), mimetype='application/json',headers={"Access-Control-Allow-Origin":'*','Access-Control-Allow-Headers':'*'})
    # check get post request params
    def checkRequestParams(self,request,params=[]):
        for v in params:
            value=request.values.get(v)
            if value is None or value==0 or value == '':
                return v
        return False
    # move the upload file to target folder
    def moveUploadFile(self,file_path,oldFile=''):
        res=file_path.split(',')
        fileName=res[0]
        targetFolder=res[1]
        currentPath = os.path.dirname(__file__)
        basePath=os.path.dirname(os.path.dirname(currentPath))
        sourcePath = basePath+'/media/temp/'+fileName
        targetPath= basePath+'/media/'+targetFolder+'/'+fileName
        if oldFile != '':
            if os.path.exists(basePath+'/media/'+oldFile) == False:
                return False
            else:
                os.unlink(basePath+'/media/'+oldFile)
        if os.path.exists(sourcePath) == False or os.path.exists(basePath+'/media/'+targetFolder) == False:
            return False
        shutil.move(sourcePath,targetPath)

        return targetFolder+'/'+fileName
    # curl pot
    def post(self,url,data={}):
        res=requests.post(url,data)
        return res.json()
    # curl get
    def get(self,url,data={}):
        args=[]
        for k in data:
            args.append(k+'='+data[k])
        if args:
            url+='?'+'&'.join(args)
        res=requests.get(url)
        return res.json()
    # 更新当前媒体用户数据
    def updateCurrentInfo(self,cols):
        db = SequoiaDB()
        orderby = {}
        where={
            "openid":cols['openid'],
            "type":cols['type'],
            "from_type":cols['from_type'],
            "parent_id":cols['parent_id']
        }
        select={}
        res = db.query('medianumbers', select, where, orderby, limit=1)
        if not res:
            db.insert(request,'medianumbers',cols)
        else:
            # print res[0].id
            res[0].update(cols, request)
    # get root path
    def root_path(self):
        # Infer the root path from the run file in the project root (e.g. manage.py)
        # fn = getattr(sys.modules['__main__'], '__file__')
        # root_path = os.path.abspath(os.path.dirname(fn))
        root_path=current_app.root_path
        return root_path

    # 生成条形统计图所需要的结构

    def getChart(self,xAxis,data):
        fansChart = {
            'xAxis': {
                'type': 'category',
                'data': xAxis
            },
            'series':[]
        }
        for i in data:
            item={
                    'name': i['name'],
                    'smooth': True,
                    'type': i['type'],
                    'data': i['data']
            }
            fansChart['series'].append(item)
        return fansChart

