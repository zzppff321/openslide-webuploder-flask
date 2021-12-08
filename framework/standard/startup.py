#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
from com.minerequest import MineAuthentic
BLUENAME, request = ('', None)

#系统启动时自动运行的处理内容，mode: 第1位代表显示模式，0-主菜单；1-子菜单；2-子菜单后面的操作项；第2位代表打开方式，0-框架页面
@MineAuthentic.auth(request, blue='workbench'+'GUI',  uid=11000, depict=u'工作总台', menu=00, icon=u'menu-i1')
@MineAuthentic.auth(request, blue='resource'+'GUI',   uid=12000, depict=u'资源管理', menu=00, icon=u'menu-i2')

@MineAuthentic.auth(request, blue='content'+'GUI',    uid=13000, depict=u'创意中心', menu=00, icon=u'menu-i3')
@MineAuthentic.auth(request, blue=BLUENAME+'data',    uid=13100, depict=u'数据概况', menu=10, remark=u'当前的所有数据表现情况')
@MineAuthentic.auth(request, blue=BLUENAME+'user',    uid=13900, depict=u'创意会员', menu=10, remark=u'所有拥有媒体账号权限的会员')
@MineAuthentic.auth(request, blue=BLUENAME+'media',   uid=13300, depict=u'媒体账号', menu=10, remark=u'各种平台发布的案例')
@MineAuthentic.auth(request, blue=BLUENAME+'auth',    uid=13400, depict=u'内容审计', menu=10, remark=u'全部会员已经发布的作品内容')

@MineAuthentic.auth(request, blue='market'+'GUI',     uid=14000, depict=u'营销数据', menu=00, icon=u'menu-i4')
#@MineAuthentic.auth(request, blue=BLUENAME+'model',   uid=14200, depict=u'数据模型', menu=10, remark=u'')
#@MineAuthentic.auth(request, blue=BLUENAME+'task',    uid=14300, depict=u'采集任务', menu=10, remark=u'')
#@MineAuthentic.auth(request, blue=BLUENAME+'data',    uid=14700, depict=u'数据资产', menu=10, remark=u'以时间维度为核心的数据管理')
#@MineAuthentic.auth(request, blue=BLUENAME+'user',    uid=14900, depict=u'用户资产', menu=10, remark=u'以用户为度为核心的数据管理，包括访问过有识别系统的平台的用户')

@MineAuthentic.auth(request, blue='apps'+'GUI',       uid=15000, depict=u'应用管理', menu=00, icon=u'menu-i5')
@MineAuthentic.auth(request, blue=BLUENAME+'apps',    uid=15200, depict=u'所有应用', menu=10, remark=u'应用站注册的小程序应用')
@MineAuthentic.auth(request, blue='plus'+'GUI',       uid=16000, depict=u'插件管理', menu=00, icon=u'menu-i6')
@MineAuthentic.auth(request, blue=BLUENAME+'plus',    uid=16100, depict=u'所有插件', menu=10, remark=u'应用站可用（有偿或无偿）的插件')
@MineAuthentic.auth(request, blue='manage'+'GUI',     uid=17000, depict=u'其他管理', menu=00, icon=u'menu-i7')
@MineAuthentic.auth(request, blue='payment'+'GUI',    uid=18000, depict=u'财务管理', menu=00, icon=u'menu-i8')
@MineAuthentic.auth(request, blue=BLUENAME+'payment', uid=18100, depict=u'交易记录', menu=10, remark=u'各应用平台的在线支付交易')
@MineAuthentic.auth(request, blue=BLUENAME+'bonus',   uid=18900, depict=u'盘古金-设置', menu=10)
@MineAuthentic.auth(request, blue=BLUENAME+'bonusli', uid=18901, depict=u'盘古金-名单', menu=20)
@MineAuthentic.auth(request, blue=BLUENAME+'bonusti', uid=18902, depict=u'盘古金-提现', menu=20)
@MineAuthentic.auth(request, blue='setting'+'GUI',    uid=19000, depict=u'系统设置', menu=00, icon=u'menu-i9')
@MineAuthentic.auth(request, blue=BLUENAME+'log',     uid=19900, depict=u'日志管理', menu=10)
@MineAuthentic.auth(request, blue='number'+'GUI',     uid=20000, depict=u'运营账号', menu=00, icon=u'menu-i9')

# @MineAuthentic.auth(request, blue=BLUENAME+'model',   uid=20200, depict=u'运营账号', menu=10, remark=u'')

def _default(): pass

#以下是只有测试环境可以使用的开发工具包，只有level为-1的超级管理员可用，且不可授权
BLUENAME = 'framework'+'GUI' #Graphical User Interface
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)

from flask import session
#session.permanent = True

from flask import request, render_template

@mod.route('', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=19999, depict=u'创建RDA模块')
def dba_build():
    if request.url.startswith('https://'): return u'', 404 #https为正式环境，不能使用此功能
    #从其他系统导入资源
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    if not Mine.level == -1: return u'', 403

    # 2. 如果是提交行为
    if request.method == 'POST':
        model = request.form.get('model', None)
        method = request.form.getlist('method')
        model = request.form.get('model', None)
        model = request.form.get('model', None)
        model = request.form.get('model', None)
        model = request.form.get('model', None)
        model = request.form.get('model', None)
        # 3. 整理数据
        # 4. 生成文件并打包

    # 5. 准备创建前的界面所需信息和内容
    #读取所有的数据模型，以供选择针对模型的模块功能创建

    HTML = render_template('build.html',brief=u'创建RDA模块', title=u'创建RDA模块', Mine=Mine)
    return HTML
