# coding:utf-8

BLUENAME = 'distribution_api_upload'
from com.distribution_api import distributionApi
import uuid

from werkzeug.utils import secure_filename
import os

BLUENAME = 'distribution_api_upload'
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)
from flask import request, render_template, redirect, url_for

appid = 20320
_var = locals()

@mod.route('/index', methods=['post'])
def upload():
    base = distributionApi()
    userinfo = base.auth()
    if userinfo == False:
        return base.error('token error',{},-2)
    res=base.checkRequestParams(request, ['type'])
    if res :
        return base.error(res+' is empty')
    f = request.files['file']
    if f is None:
        return base.error('upload file is empty')
    currentPath = os.path.dirname(__file__)  # 当前文件所在路径
    basePath = os.path.dirname(currentPath)
    floder='media/temp'
    suffiex=os.path.splitext(f.filename)[1]
    newName=uuid.uuid4().hex+suffiex
    upload_path = os.path.join(basePath, floder, secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
    f.save(upload_path)
    newpath=basePath+'/'+floder+'/'+newName
    os.rename(upload_path,newpath)
    return base.success({
        'filepath':newName+','+request.form['type'],
    })