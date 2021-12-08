#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
#-*- coding:utf-8 -*-

BLUENAME = 'fs'+'AGI' #Application Gateway Interface       #系统内部使用的网关，主要应用于系统需要的ajax读取
#BLUENAME = 'rfs'+'API' #Application Programming Interface   #公共应用接口，主要应用于内外部系统的统一读写操作管理
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)

from flask import session
#session.permanent = True

#外部系统上传文件接口
'''
客户端（即：外部系统）POST方式发送文件流数据给rfs
rfs处理后，回传给客户端文件的存储标记（即：_id）和访问地址
rfs处理时，计算文件的hash值（MD5），重复的递增文件记录使用者数量，不重复的将文件保存在硬盘系统中
'''
#外部系统获取文件信息接口
'''
文件数据库信息首次访问时保存到cache里，并设置浏览次数和最后浏览时间戳
每次被获取时都更新次数（递增+1）和最后浏览时间
当次数达到或超过限定阀值（一般为100次）时，或者最后浏览时间超过限定阀值时长（一般为30分钟）时，通过线程处理同步更新数据库数据
'''
#外部系统删除文件接口


from flask import request
from com import utils

from com.sf import StreamFileLocal

def upload_ajax(request, ip=None):
    #文件上传
    if not request.method == "POST": return '<h2>500 Operation mode is not correct</h2>', 500
    
    f = StreamFileLocal({"$stream":request.data}, req=request)
    return f.save().name

def upload_file(request, ip=None):
    #文件上传
    if not request.method == "POST": return u'<h2>500 Operation mode is not correct</h2>', 500
    
    f = StreamFileLocal({"$stream":request.data}, req=request)
    return f.save().name

#文件上传测试
def test_step1(request, ip=None):
    return '''
<!doctype html><title>Upload new File</title><h1>Upload new File</h1>
<form action="/wservice@fs?method=upload" method=post enctype=multipart/form-data>
  <p><input type=file name=file><input type=submit value=Upload></p>
</form>
'''
def _default(request): return u'', 404
def test(request, ip=None): return u'This http is ok!'

@mod.route('', methods=['POST'])#, 'GET']) #GET方式仅DEBUG模式使用
#主函数，因为有其他平台接入的可能性，所以不验证登录用户权限，以后改成验证来源权限 wht20191021
#还是用本地上传管理的方式，其他平台接入的方法再另外考虑新的模块
def opera_main():
    Mine = request.Mine()
    if not Mine.is_online: return u'', 401
    #统一的访问入口
    define = {
        'send': upload_ajax,
        'upload': upload_file,
        'test': test_step1
    }

    method = request.args.get('method', 'test')
    if not method in define: return _default(request)
    
    ip = utils.get_ipaddress(request)

    return define[method](request, ip=ip) #需要传入request.post，避免开发测试时使用GET数据后，生产环境忘记修改
