#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8

BLUENAME = 'account'+'GUI' #Graphical User Interface
from flask import Blueprint
mod = Blueprint(BLUENAME, __name__)

from flask import session
#session.permanent = True

from flask import request, render_template, redirect, url_for
from com.db import SequoiaDB
from com.minerequest import MineAuthentic
from com.pinyin import Pinyin
from standard import WWX
import requests

appid = 19100
_var = locals()
from collections import OrderedDict
_where = {"depart":OrderedDict([('$type', 1), (u'$et', 4)])} #wxid可能以后会用到个人微信的登录，但部门只有企业微信可以获取

@mod.route('/update-address-book', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+9, depict=u'更新通讯录')
def opera_update_address_book():
    #账户列表
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    if not Mine.level == -1: return '400'
    # 0. 特殊环节，用于获取所有企业微信账户并保存到数据库
    WWX.get_accesstoken(WWX.wx_corpid, "qkV9qPGfWzfGOY1W4CqRm1LS51O_J0rniq8Ot_bg7tM")
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list'
    req = requests.get(url, params={"access_token":WWX.access_token, "department_id":1, "fetch_child":1})
    ul = []
    weixi_query = {}
    t,a,u,i = 0,0,0,0
    if req.status_code == requests.codes.ok:
        for wxinfo in req.json().get("userlist"):
            t += 1 #用户总量增量
            if not wxinfo: continue
            wxid = wxinfo.get("userid", u'')
            if wxid == u'': continue
            weixi_query[wxid] = wxinfo

    msgList = []

    db = SequoiaDB()
    #微信账户有效，需要将微信账户与系统账户对应
    select = {"status":"", "realname": "", "wxid": ""}
    where  = {"wxid": {"$isnull": 0}}

    query = {}
    for q in db.query("users", select, where, {}):
        query[q.wxid] = q

    for wxid, wxinfo in weixi_query.items():
        a += 1 #有效id增量

        #如果微信账户第一次登录或者被强制删除系统账户，则需要录入账户信息
        realname = wxinfo["name"]
        for k in ("（", "(", "-", "~"):
            if realname.find(k) > 0: realname = realname[:realname.find(k)]
        py = Pinyin()
        pinyin = py.pinyin(realname)
        mailbox = wxinfo["email"]
        if mailbox == u'': mailbox = u'e-%s@panguweb.cn' % pinyin

        q = query.get(wxid, None)
        if q is None:
            data = {
                u"wxid":    wxinfo["userid"],
                u"uuid":    u"9"+u"0"*(17-len(wxinfo["mobile"]))+wxinfo["mobile"],
                u"account": u"wx_%s" % wxinfo["userid"],
                u"pasword": u"",
                u"realname":realname,
                u"pinyin":  pinyin,
                u"gender":  int(wxinfo["gender"]),
                u"mailbox": mailbox,
                u"mobile":  wxinfo["mobile"],
                u"depart":  wxinfo["department"],
                u"face":    wxinfo["avatar"],
                u"status":  405 #默认新用户需要审核后才可以使用系统
            }
            desc = u'更新通讯录时导入企业微信用户【%s】。%s' % (data["realname"],wxid)
            try:
                db.insert(request, "users", data=data, event_desc=(1000, desc), laissez_passer=[u'uuid'])
                msgList.append(u'<div>(%s)%s【%s】，注册成功！</div>' % (wxid,data["realname"],wxinfo["mobile"]))
            except Exception as e:
                i -= 1
                msgList.append(u'<div>(%s)%s【%s】，发生错误！%s，%s</div>' % (wxid,data["realname"],wxinfo["mobile"], e, data))
            i += 1
        else:
            data = {
                u"realname":realname,
                u"gender":  int(wxinfo["gender"]),
                u"mailbox": mailbox,
                u"mobile":  wxinfo["mobile"],
                u"depart":  wxinfo["department"],
                u"face":    wxinfo["avatar"]
            }
            desc = u'更新通讯录时刷新账户【%s】的信息。%s' % (data["realname"],wxid)
            try:
                q.update(data, request, event_desc=(1000, desc))
                msgList.append(u'<div>(%s)%s【%s】，资料更新！</div>' % (wxid,data["realname"],wxinfo["mobile"]))
            except Exception as e:
                u -= 1
                msgList.append(u'<div>(%s)%s【%s】，更新错误！%s，%s</div>' % (wxid,data["realname"],wxinfo["mobile"], e, data))
            u += 1
            #删除记录，标示账户有效，剩下的就是无效的
            del query[wxid]
    msgList.insert(0, u'<p>获取%s人，无效%s人，更新%s人，登记%s人</p>' % (t, t-a, u, i))

    t = 0
    for wxid,q in query.items():
        t += 1
        q.update({"status":0}, request, event_desc=(1000, u'更新通讯录时撤销无效账户【%s】。%s' % (q.realname,wxid)))
    msgList.insert(0, u'<p>撤销无效账户%s人</p>' % t)

    return u''.join(msgList)

@mod.route('/list', methods=['GET'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+0, depict=u'业务账户', menu=10)
def opera_list():
    #账户列表
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    #if not Mine.level == -1: return '400'
    # 2. 获取外部GET方式传入的条件等筛选配置
    # 2.1 获取翻页条的页码和配置
    page = request.args.get('p', u'1')
    size = request.args.get('s', u'') # 默认每页显示20条数据
    try:
        page = int(page)
    except:
        page = 1
    try:
        size = int(size)
    except:
        size = 20
    # 2.2 条件等筛选配置保存到so变量中，并传入模版展示到页面
    so = { u'kt':u'', u'kw':u'', u'wxid':u'', u'status':u'' }
    # 2.3 获取筛选条件选项的值
    for k,v in so.items():
        _var[k] = so[k] = request.args.get(k, v)
    shis = 'flase' # 用来控制历史搜索是否展示
    # 3. 查询数据
    db = SequoiaDB()
    # 3.1 定义查询需要的变量及默认设置
    query = []
    select = {"realname":"", "wxid":"", "gender":"", "location":"", "level":"",
              "leader1":"", "leader2":"", "leader3":"", "leader4":"", "leader5":"", 
              "mobile":"", "status":""}
    where = dict({"status": {"$in": (200, 206, 403, 405)}}, **_where)
    #默认，按添加时间倒序排列，即新用户在前
    orderby = {"level":-1, "status":1}
    #3.2 组合查询条件
    if not kw == u'':
        if   kt == u'1':
            where['$or'] = [
                {"realname": {"$regex": '%s' % kw, "$options": 'i'}},
                {"pinyin":   {"$regex": '%s' % kw, "$options": 'i'}},
            ]
        elif kt == u'2':
            where['$or'] = [
                {"wxid":     {"$regex": '%s' % kw, "$options": 'i'}},
            ]
    else:
        shis = 'true'
    if not wxid == u'':
        if   wxid == u'1': where['wxid'] = {"$isnull": 0}
        elif wxid == u'2': where['wxid'] = {"$isnull": 0}
    if not status == u'':
        try:
            where['status'] = int(status)
        except:
            pass
    #用户管理中不可以管理自己的账户信息
    where['-id'] = (Mine.id,)
    if wxid == u'2':
        where['leader1'] = u''
        where['leader2'] = u''
        where['leader3'] = u''
        where['leader4'] = u''
        where['leader5'] = u''
        where['level'] = 0
    elif not Mine.level == -1:
        where["_id"] = Mine.staff()

    #3.3 查出数据并保存到向模版发送的变量（一般设置为data或具体代表数据含义的变量名称）
    #如果查询发现没有集合存在，出现报错时，直接跳转到编辑页面进行添加
    if not db.hascl('users'): return redirect(url_for('%s.opera_edit' % BLUENAME))
    query = db.pagebar('users', select, where, orderby, so, [size, page])
    
    #设置一个索引，用于获取某些特定数据标记的名称
    Index = {}
    _w = {"status": {"$in":(200,206)}, "level":{"$in":(1,2,3,4,5,-1)}}
    for q in db.query('users', {"realname":""}, _w, {}):
        Index[q.id] = len(q.realname) == 2 and u'%s　%s' % (q.realname[0],q.realname[1]) or q.realname

    _w = {"level":2}
    for q in db.query('location', {"id":"", "depict":""}, _w, {"id":1}):
        Index[q.id] = q.depict

    #列出可认领的员工名单，这些名单只是授权使用了，但并没有设置归属上级和其他资料
    users = []
    _w = {"status":200, "wxid":{"$isnull": 0}, "level":0, "leader1":'',"leader2":'',"leader3":'',"leader4":'',"leader5":''}
    if not kw == u'':
        if   kt == u'1':
            _w['$or'] = [
                {"realname": {"$regex": '%s' % kw, "$options": 'i'}},
                {"pinyin":   {"$regex": '%s' % kw, "$options": 'i'}},
            ]
        elif kt == u'2':
            _w['$or'] = [
                {"wxid":     {"$regex": '%s' % kw, "$options": 'i'}},
            ]
    for q in db.query('users', select, _w, orderby):
        users.append(q)

    HTML = render_template('users/list.html',
                           query=query, users=users, Index=Index, so=so, title=u'所有账户_用户管理', Mine=Mine)
    return HTML

@mod.route('/auth', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+6, depict=u'扫码授权')
def opera_auth():
    #审核企业微信扫码的新账户登录资格
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    if not Mine.level == -1: return '400'
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    
    db = SequoiaDB()
    # 3. 查询指定id的数据
    Q = None
    # 3.1 定义查询需要的变量及默认设置
    select = {"realname":"", "wxid":"", "addtime":"", "status":""}
    where = dict({"_id":(id,), "-id":(Mine.id,), "status":405}, **_where)#只有状态为待授权的微信账户才可以授权
    # 3.2 开始查询
    if id == u'': return u'请用规范的方式使用本系统！'
    for q in db.query('users', select, where, {}, limit=1):
        Q = q
        break
    if Q is None: return u'您要执行的操作被拦截啦！'
    _brief = u'给账户【%s】授权' % Q.realname
    # 4. 如果是提交行为
    if request.method == 'POST':
        data = {"status":200} #默认授权后的状态为200
        remark = request.form.get('remark', u'')
        if remark == u'': return u'请确认授权的说明！'
        # 4.1 判断当前登录的用户是否有权限授权本数据
        
        # 4.2 更新所有下级关联的数据记录（逻辑/物理）
        
        # 4.3 执行操作（逻辑/物理）
        Q.update(data, request, event_desc=(1000, u'授权企业微信可登录'))

        # 4.4 处理其他上级关联的统计数据

        return redirect(url_for('%s.opera_list' % BLUENAME))
    # 5. 需要显示内容的其他调整

    HTML = render_template('users/auth.html',
                           Q=Q, brief=_brief, title=u'企业微信授权_用户管理', Mine=Mine)
    return HTML

@mod.route('/right', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+5, depict=u'权限管理')
def opera_right():
    #审核企业微信扫码的新账户登录资格
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    if Mine.level not in (-1,2,3,4,5): return u'您不能为账户分配权限！'
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    if not Mine.level == -1 and id not in Mine.staff(): return u'您只能为自己下级员工授权！'
    
    db = SequoiaDB()
    # 3. 查询指定id的数据
    Q = None
    # 3.1 定义查询需要的变量及默认设置
    select = {"realname":"", "wxid":"", "uuid":"", "rights":"", "addtime":"", "status":""}
    where = dict({"_id":(id,), "-id":(Mine.id,), "status":200}, **_where) #只有状态为待授权的微信账户才可以授权
    # 3.2 开始查询
    if id == u'': return u'请用规范的方式使用本系统！'
    for q in db.query('users', select, where, {}, limit=1):
        Q = q
        break
    if Q is None: return u'您要执行的操作被拦截啦！'
    if Q.uuid[0] == u'9': return u'请先修改账户资料，完善身份信息！'
    _brief = u'给账户【%s】授权' % Q.realname
    if not isinstance(Q.rights, list): Q.rights = [] #right记录拥有的权限的uid，默认注册时可能是u''（空）
    #从系统中读取所有的可执行权限，只能分配自己有的权限
    Ri = MineAuthentic.getlist()
    Rights = []
    if Mine.level == -1:
        Rights = Ri
    else:
        for ri in Ri:
            if ri[0] in Mine.rights: Rights.append(ri)
    # 4. 如果是提交行为
    if request.method == 'POST':
        data = {}
        # 4.1 对序列化的数据进行验证
        ri = request.form.getlist('ri')
        remark = request.form.get('remark', u'')
        # 4.2 验证每项数据有效性和存储格式
        if remark == u'': return u'请确认冻结的说明！'
        # 整理权限的uid，自动存储上级uid
        rights = []
        for x in Rights:
            if str(x[0]) in ri:
                rights.append(x[0])
                if (x[0] / 100) * 100 not in rights:
                    rights.append((x[0] / 100) * 100)
                if (x[0] / 1000) * 1000 not in rights:
                    rights.append((x[0] / 1000) * 1000)
        rights.sort()
        # 4.3 执行操作（逻辑/物理）
        data["rights"] = rights
        Q.update(data, request, event_desc=(1000, u'授权可执行权限：%s' % remark))

        # 4.4 处理其他上级关联的统计数据

        return redirect(url_for('%s.opera_list' % BLUENAME))
    # 5. 需要显示内容的其他调整

    HTML = render_template('users/right.html',
                           Q=Q, Rights=Rights, brief=_brief, title=u'企业微信授权_用户管理', Mine=Mine)
    return HTML

@mod.route('/lock', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+99, depict=u'账户状态管理')
def opera_lock():
    #删除资源（*** 物理删除 ***）
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    if not Mine.level == -1: return '400'
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    
    db = SequoiaDB()
    # 3. 查询指定id的数据
    Q = None
    # 3.1 定义查询需要的变量及默认设置
    select = {"realname":"", "wxid":"", "addtime":"", "status":""}
    where = dict({"_id": (id,), "-id":(Mine.id,)}, **_where)
    # 3.2 开始查询
    if id == u'': return u'请用规范的方式使用本系统！'
    for q in db.query('users', select, where, {}, limit=1):
        Q = q
        break
    if Q is None: return u'您要执行的操作被拦截啦！'
    _brief = Q.status == 0 and u'解除【%s】的冻结状态' % Q.realname or u'冻结账户【%s】' % Q.realname
    # 4. 如果是提交行为
    if request.method == 'POST':
        remark = request.form.get('remark', u'')
        if remark == u'': return u'请确认冻结的说明！'
        # 4.1 判断当前登录的用户是否有权限删除本数据
        
        # 4.2 删除所有下级关联的数据记录（逻辑/物理）
        
        # 4.3 执行删除（逻辑/物理）
        operater = '%s' % Mine
        if Q.status == 0:
            data = {"status":200}
            desc = u'解除账户【%s】的冻结状态：%s' % (Q.realname, remark)
        else:
            data = {"status":0}
            desc = u'将账户【%s】执行冻结账户处理：%s' % (Q.realname, remark)
        Q.update(data, request, event_desc=(1000, desc))
        # 4.4 处理其他上级关联的统计数据
        
        # 4.5 删除数据关联的物理文件，仅限数据 物理 删除时执行

        return redirect(url_for('%s.opera_list' % BLUENAME))

    # 5. 需要显示内容的其他调整

    HTML = render_template('users/lock.html',
                           Q=Q, brief=_brief, title=u'冻结账户_用户管理', Mine=Mine)
    return HTML

@mod.route('/edit', methods=['GET', 'POST'])
@MineAuthentic.auth(request, blue=BLUENAME, uid=appid+1, depict=u'编辑资料')
def opera_edit():
    #编辑账户资料
    Mine = request.Mine()
    # 1. 验证权限，【已经整合到装饰器MineAuthentic类】
    # 2. 获取被编辑对象的id
    id = (not request.form.get('id', u'') == u'') and request.form.get('id', u'') or request.args.get('id', u'')
    
    db = SequoiaDB()
    # 3. 查询指定id的数据
    Q = None
    # 3.1 定义查询需要的变量及默认设置
    select = {"realname":"", "wxid":"", "uuid":"", "location":"", "level":"", 
              "leader1":"", "leader2":"", "leader3":"", "leader4":"", "leader5":"", 
              "mailbox":"", "mobile":"", "gender":"", 
              "adder":"", "addtime":"", "status":""}
    where = dict({"_id": (id,), "-id":(Mine.id,), "status": {"$in": (200, 206)}}, **_where) #只有状态为正常的才可以编辑
    # 3.2 开始查询
    if id == u'':
        _brief = u'开通新账号'
        return u'只能通过平台或企业微信扫码注册账号，您要执行的操作被拦截啦！'
    else:
        for q in db.query('users', select, where, {}, limit=1):
            Q = q
            break
        if Q is None: return u'请确认账户的状态是否正常，您要执行的操作被拦截啦！'
        _brief = u'编辑【%s】的账号资料' % Q.realname
    if u''.join((Q.leader1,Q.leader2,Q.leader3,Q.leader4,Q.leader5)) == u'' and Q.level == 0 and not Q.wxid == u'':
        pass
    else:
        if not Mine.level == -1 and Q.id not in Mine.staff(): return u'您只能修改自己下级员工的资料！'
    # 4. 如果是提交行为
    if request.method == 'POST':
        #只能编辑自己下级员工的资料
        data = {}
        checkbit = ("rights", )
        # 4.1 获取表单提交的数据，为了保证多选数据可以正确获取，分别使用get和getlist，再每一项验证格式和数据
        for k,v in select.items():
            if k in ("adder", "addtime", "status"): continue
            if k in checkbit:
                data[k] = request.form.getlist(k)
            else:
                data[k] = request.form.get(k,v)
        # 4.2 验证每项数据有效性和存储格式
        require = (
            ("realname",u'姓名不能为空，且字符不得过长！',8),
            ("uuid",u'请输入正确的身份证号码！',18),
            ("location",u'请选择员工工作所在地区！',float("inf")),
            ("level",u'请选择员工主管等级！',1),
            ("mobile",u'手机号码不能为空，且为标准11位数字！',11)
        )
        default = (
            ("gender", Q.gender),
        )
        digited = (
            (int, "location",u'[location]出错啦！'),
            (int, "level",   u'[level]出错啦！'),
            (int, "gender",  u'[gender]出错啦！'),
        )
        #判断必填项是有空值
        for k,tips,l in require:
            if data[k] == u'' or len(data[k]) == 0: return tips
            if len(data[k]) > l: return tips
        #设置必要的默认值
        for k,v in default:
            if data[k] == u'': data[k] = v
        #判断数据类型是否符合要求
        for func,k,tips in digited:
            if isinstance(data[k], list):
                v = []
                for x in data[k]:
                    d = u'0%s' % x
                    if not d.isdigit(): return tips
                    v.append(func(d))
            else:
                d = u'0%s' % data[k]
                if not d.isdigit(): return tips
                v = func(d)
            data[k] = v
        #验证是否重复的数据
        for q in db.query('users', {"status":""}, {"uuid": data["uuid"], "-id":(id,)}, {}, limit=1):
            return u'身份证号码【%s】已经存在，请重新编辑！' % data["uuid"]
        for q in db.query('users', {"status":""}, {"uuid": data["mobile"], "-id":(id,)}, {}, limit=1):
            return u'手机号【%s】已经存在，请重新编辑！' % data["mobile"]
        #验证属性是否有效
        _O = None
        for q in db.query('location', {"status":""}, {"id": data["location"]}, {}, limit=1):
            _O = q
        if _O is None: return u'您选择的员工所在地区不正确！'
        if data["level"] not in (0,1,2,3,4,5): return u'您选择的员工主管等级不正确！'
        if (not Mine.level == -1) and data["level"] >= Mine.level: return u'您选择的员工主管等级已超出您的范围！'
        #优化汇报关系，不能有低于level级别的上级
        for x in range(0, data["level"]):
            data["leader%s" % (x+1)] = u''
        #设置发布人
        operater = '%s' % Mine
        ipaddres = Mine.get_ipaddress(request)

        # 4.3 写数据
        if Q is None:
            #账号不能通过管理站注册
            pass
        else:
            #更新已有数据
            Q.update(data, request, event_desc=(1000,u'编辑【[%s]%s】的资料' % (Q.id, Q.realname)))

        return redirect(url_for('%s.opera_list' % BLUENAME))

    # 5. 需要显示内容的其他调整
    if Q.uuid[0] == u'9': Q.uuid = u''
    Location = []
    _w = {"level":2, "id":OrderedDict([("$cast","string"), ("$substr",[0,2]), ("$in",['12','13','21','22'])])}
    for q in db.query('location', {"id":"", "depict":""}, _w, {}):
        Location.append(q)
    Leader = []
    for q in db.query('users', {"realname":"", "level":""}, {"status": {"$in": (200, 206)}, "level":{"$in":(1,2,3,4,5,-1)}, "-id":(id,)}, {"level":1}):
        Leader.append(q)

    HTML = render_template('users/edit.html',
                           Q=Q, Location=Location, Leader=Leader, brief=_brief, title=u'编辑模版_资源管理', Mine=Mine)
    return HTML