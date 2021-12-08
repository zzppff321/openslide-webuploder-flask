#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
from types import MethodType
from flask.globals import request
import time
from bson import ObjectId
import openslide,os,hashlib,json
from com.distribution_api import distributionApi
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(1)

BLUENAME = 'distribution_split'
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)
# from flask import session
# session.permanent = True

# from flask import request, render_template, redirect, url_for
# from com.db import SequoiaDB
# from com.minerequest import MineAuthentic
# from com.sf import StreamFileLocal
# from com import utils
# import config

rootPath='/var/www/html/videoSending/media/'
appid = 20320
_var = locals()
# 图像分片上传初始化
@mod.route('/upload/init',methods=['get'])
def uploadInit():
    string = 'zaq1xsw2QWER!@#$'
    task_id  = hashlib.md5(string.encode('utf8')).hexdigest()
    dir = rootPath+'microscope/'+task_id
    if os.path.isdir(dir) == False:
        os.mkdir(dir)
        os.mkdir(dir+'/img')
    return distributionApi().success({'task_id':task_id})
# 分片上传 
@mod.route('/upload',methods=['post'])
def upload():
    res = distributionApi().checkRequestParams(request,[
        'task_id'
    ])
    if res :
        return distributionApi().error(res+'不能为空')
    task_id = request.form.get('task_id')
    dir = rootPath+'microscope/'+task_id
    if os.path.isdir(dir) == False:
        return distributionApi().error('id不存在,请进行分片上传初始化')
    upload_file = request.files['file']
    chunk = request.form.get('chunk', 0)        # 获取该分片在所有分片中的序号
    filename = '%s.%s' % (task_id, chunk)           # 构成该分片唯一标识符
    tmp_dir= dir+'/tmp/'
    if os.path.isdir(tmp_dir) == False:
        os.mkdir(tmp_dir)
    upload_file.save(tmp_dir+'%s' % filename)
    return distributionApi().success({},'分片上传成功')
#  文件上传完成
@mod.route('/upload/finish',methods=['get'])
def uploadFinish():
    # target_filename = request.args.get('filename')  # 获取上传文件的文件名
    target_filename = 'base.ndpi'
    task_id = request.args.get('task_id')              # 获取文件的唯一标识符
    chunk = 0                                       # 分片序号
    with open(rootPath+'microscope/'+task_id+'/%s' % target_filename, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = rootPath+'microscope/'+task_id+'/tmp/%s.%d' % (task_id, chunk)
                source_file = open(filename, 'rb')                    # 按序打开每个分片
                target_file.write(source_file.read())                 # 读取分片内容写入新文件
                source_file.close()
            except IOError:
                break
            chunk += 1
            os.remove(filename)                     # 删除该分片，节约空间
    return distributionApi().success({},'上传完成')
        
# 图像分割进度查询
@mod.route('/count',methods=['get'])
def count():
    task_id = request.args.get('task_id',type=str,default='')
    if task_id =='':
        return distributionApi().error('id不能为空')
    # 文件大小
    # totalSize=0 文件大小
    fileNum=0 
    # dirNum=0
    dir = rootPath+"microscope/"+task_id
    path = dir+"/img"
    f = open(dir+"/config.json")
    content = f.read()
    f.close()
    config = json.loads(content)

    for lists in os.listdir(path):
        sub_path = os.path.join(path, lists)
        # print(sub_path)
        if os.path.isfile(sub_path):
            fileNum = fileNum+1                      # 统计文件数量
            # totalSize = totalSize+os.path.getsize(sub_path)  # 文件总大小
        # elif os.path.isdir(sub_path):
            # dirNum = dirNum+1                       # 统计文件夹数量
            # visitDir(sub_path)       
    return distributionApi().success({
        'total':config['count'],
        'done':fileNum
    })
# 图像分割创建配置文件并返回结果
@mod.route('/split',methods=['get'])
def splitIndex():

    res = distributionApi().checkRequestParams(request,[
        'task_id',
        'height',
        'width',
        'minUnit'
    ])
    if res :
        return distributionApi().error(res+'不能为空')
    task_id=request.args.get('task_id',type=str,default='')
    h=request.args.get('height',type=int,default=0)
    w=request.args.get('width',type=int,default=0)
    minUnit=request.args.get('minUnit',type=int,default=0)
    if (h-minUnit) <= 0 or (w-minUnit) <= 0:
        return distributionApi().error('长宽均不得小于最小切割单元')
    img_dir = rootPath+"microscope/"+task_id
    img_path = img_dir+"/base.ndpi"
    if os.path.exists(img_path) == False:
        return distributionApi().error('指定id文件不存在')
    slide = openslide.open_slide(img_path)
    # 获取ndpi文件尺寸
    size=slide.dimensions
    # 计算切割文件数量
    x=0
    count=0
    while x+w < size[0]:
        y=0
        while y + h < size[1]:
            count+=1
            y+=(h-minUnit)
        x+=(w-minUnit)  
    slide.close()
    # 生成配置文件
    config={
        'task_id':task_id,
        'width':w,
        'height':h,
        'minUnit':minUnit,
        'ndpiInfo':{
            'width':size[0],
            'height':size[1]
        },
        'count':count
    }
    f = open(img_dir+"/config.json", "w+")
    f.write(json.dumps(config))
    f.close()
    executor.submit(split,h,w,minUnit,img_dir)
    return distributionApi().success({},'配置文件生成完毕，图像分割中')
# 图像分割后台任务
def split(h,w,minUnit,img_dir):
    #切片路径
    img_path = img_dir+"/base.ndpi"
    #打开
    slide = openslide.open_slide(img_path)
    #获取长宽
    size=slide.dimensions
    print (size)
    x=0
    i=0
    while x+w < size[0]:
        print (x+w)
        y=0
        j=0
        while y + h < size[1]:
            tile=slide.read_region([x,y],0,[w,h])
            tile.save(img_dir+'/img/'+str(j)+'-'+str(i)+".jpg")
            print (x,y,x+w, y+h)
            y+=(h-minUnit)
            j+=1
        x+=(w-minUnit)  
        i+=1

    # cols=size[0]/w
    # rows=size[1]/h
    # while j < rows:
    #     i = 0
    #     x = 0 
    #     while i < cols:
    #         print (x, y, x+w, y+h)
    #         tile=slide.read_region([x,y],0,[w,h])
    #         tile.save(img_dir+'/img/'+str(j)+'-'+str(i)+".jpg")
    #         i += 1
    #         x += w
    #     j += 1 
    #     y += h
    slide.close()
    