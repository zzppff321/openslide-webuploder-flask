#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import time
import hashlib
import time
from bson import ObjectId
from com.distribution_api import distributionApi

BLUENAME = 'distribution_api_login'
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

@mod.route('/login', methods=['POST'])
def login():
    base=distributionApi()
    # 2.3 获取筛选条件选项的值
    db = SequoiaDB()
    if not db.hascl('opratenumbers'):
        db.create('opratenumbers')
    select = {}
    tel = request.form['tel']
    password= hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
    where = {"tel":tel,"password":password}
    orderby = {}
    res = db.query('opratenumbers', select, where, orderby, limit=1)
    if not res:
        return base.error('账号密码不正确')
    else:
        # print res[0].id
        cols={
            "token":hashlib.md5(str(time.time())+res[0].id).hexdigest()
        }
        res[0].update(cols, request, event_desc=(1000, u'用户登录[%s]' % res[0].id))
        row=db.query('opratenumbers', {"id":"","token":"","tel":""}, where, orderby, limit=1)
        return base.success(cols,'登录成功')
