#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/framework')
from datetime import timedelta
from flask import Flask, session

app = Flask(__name__, static_folder='media', static_url_path='')
app.secret_key = 'A0Zr98j/3yX R~XEH!jmN]LWX/,?RT'
#app.permanent_session_lifetime = timedelta(minutes=8*60)
#session.permanent = True

import standard
app.register_blueprint(standard.mod, url_prefix='/')
from standard import startup, users, fs, wx
app.register_blueprint(standard.startup.mod, url_prefix='/framework')   #用于显示功能菜单
app.register_blueprint(standard.fs.mod, url_prefix='/wservice@fs')
app.register_blueprint(standard.wx.mod, url_prefix='/wservice@wx')      #企业微信通讯录更新接口
app.register_blueprint(standard.users.mod, url_prefix='/setting/user')

import users
app.register_blueprint(users.mod, url_prefix='/user')

import resource
from resource import template, material, scheme, module
from resource import server
app.register_blueprint(resource.server.mod, url_prefix='/resource/server')
app.register_blueprint(resource.template.mod, url_prefix='/resource/template')
app.register_blueprint(resource.material.mod, url_prefix='/resource/material')
app.register_blueprint(resource.scheme.mod, url_prefix='/resource/scheme')
app.register_blueprint(resource.module.mod, url_prefix='/resource/module')
#app.register_blueprint(resource.agi.mod, url_prefix='/gateway@resource')

import content
from content import product
app.register_blueprint(content.product.mod, url_prefix='/content/product')

import work
import work.taskcard
import work.taskcard.wx
app.register_blueprint(work.taskcard.mod, url_prefix='/taskcard')
app.register_blueprint(work.taskcard.wx.mod, url_prefix='/taskcard/wservice@wx')      #企业微信应用消息接收接口

#Add new model url
from datacenter import datasource,datapacket,accountgroup,account,spidergroup,spider,api,schedule
app.register_blueprint(datasource.mod,url_prefix='/datacenter/datasource')
app.register_blueprint(datapacket.mod,url_prefix='/datacenter/datapacket')
app.register_blueprint(accountgroup.mod,url_prefix='/datacenter/accountgroup')
app.register_blueprint(account.mod,url_prefix='/datacenter/account')
app.register_blueprint(spidergroup.mod,url_prefix='/datacenter/spidergroup')
app.register_blueprint(spider.mod,url_prefix='/datacenter/spider')
app.register_blueprint(api.mod,url_prefix='/datacenter/api')
app.register_blueprint(schedule.mod,url_prefix='/datacenter/schedule')

#Add new model url
from distribution import operating,media,source,publishsource
app.register_blueprint(operating.mod,url_prefix='/distribution/operating')
app.register_blueprint(media.mod,url_prefix='/distribution/media')
app.register_blueprint(source.mod,url_prefix='/distribution/source')
app.register_blueprint(publishsource.mod,url_prefix='/distribution/publishsource')
# distribution api
from distribution import api_login,api_video,api_upload,api_platform,split
app.register_blueprint(api_login.mod,url_prefix='/distribution/api_login')
app.register_blueprint(api_video.mod,url_prefix='/distribution/api_video')
app.register_blueprint(api_upload.mod,url_prefix='/distribution/api_upload')
app.register_blueprint(api_platform.mod,url_prefix='/distribution/api_platform')
app.register_blueprint(split.mod,url_prefix='/distribution/split')


'''
import cron
#任务跟踪监视器启动，必须在所有定义全部加载完毕以后
from com.daemon import MonitorStart
#MonitorStart(u'Track', os.path.dirname(os.path.abspath(__file__)))
'''
from com.minerequest import MineAuthentic
#MineAuthentic.debug(app.url_map._rules)
MineAuthentic.reorganize()


from com import filter
filter.initialize(app)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',port=5000)
    # , ssl_context = 'adhoc'












