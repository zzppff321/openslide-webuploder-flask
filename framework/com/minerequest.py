# coding=utf-8
import uuid
from functools import wraps
from hashlib import md5
from werkzeug.contrib.cache import MemcachedCache
try:
    from flask import session, redirect, render_template
except:
    raise Exception('Please install Flask.')

from com.db import SequoiaDB
from com import utils
import config, choices

cache = MemcachedCache([config.cache[1]])

#          基本操作   报表      上传       基本管理     高级管理    特殊权限
allfunc = ('opera', 'report', 'upload', 'regulate', 'manage', 'espec', 'dba')

class MineAuthentic():
    "账户操作权限验证类"
    """
根据用户的level来确定用户可以使用哪些功能
    """
    _define = {}
    _listor = None
    def debug(self, rules):
        print('#---MineAuthentic.Blue---%s------' % utils.dt.msecdate())
        for x in self.__class__._define:
            print( x )
        print('#---MineAuthentic.Rule---%s------' % utils.dt.msecdate())
        conf = {}
        for x in rules:
            conf[x.rule] = [md5(x.rule).hexdigest(),]
            print( conf[x.rule][0], x.rule )

    def getlist(self):
        if self._listor is None: raise Exception('Please execute a reorganize function in app.py.')
        return self.__class__._listor

    def reorganize(self):
        _bn, _ri = ({}, [])
        for bn, ri in self.__class__._define.items():
            _bn[bn] = ri[0]
            if ri[0] == 0: continue
            _ri.append(ri)
        _ri.sort(key = lambda x:x[0])
        self.__class__._define = _bn
        self.__class__._listor = _ri

    def startup(self, blue=None, func=None, uid=None, depict=None, remark=None, menu=None, icon=u'ico-blank'):
        #初始化所有的URL蓝图及对应权限配置
        if blue is None: raise Exception('BlueName configure param mode faild.')
        target, player = (None, None)
        if isinstance(menu, int): target, player = (menu % 10, menu / 10)
        bn = '%s.%s' % (blue, func)
        if remark is None: remark = depict
        if uid is None: return 0
        #一个uid可以对应多个URL的蓝图
        self.__class__._define[bn] = (uid, depict, remark, icon, player, target, bn)

    def auth(self, request, **configure):
        def decorator(func):
            configure['func'] = func.__name__
            self.startup(**configure)
            @wraps(func)  # 此处必须有，按照Flask规则，避免route重复装饰本类
            def wrapper(*args, **kwargs):
                # 每个方法的权限验证装饰
                # 1. 验证方法定义合法性
                # 1.1 获取当前方法信息
                f = func.__name__
                func_head = f[:f.find('_')]
                if func_head not in allfunc:
                    raise Exception("The definition of routing method can only be (opera, report).")
                # 2. 获取当前用户实例
                Mine = request.Mine()
                # 2.1 验证用户登录状态，未登录则调转至登录界面
                if not Mine.is_online: return redirect('/')
                _dif = 1000000 * 60 * 60 * 3 #即超过3小时
                if utils.dt.timestamp() - Mine.timestamp > _dif: Mine.reload(request)

                # 3. 验证用户权限
                blue = configure.get('blue', None)
                if blue is None: raise Exception('BlueName configure param mode faild.')
                bn = '%s.%s' % (blue, f)
                ri = self.__class__._define.get(bn, None)
                if ri is None: raise Exception('The developer has not written %s code.' % bn)
                if (not ri == 0) and (not Mine.level == -1):
                    #验证用户是否具备使用当前功能的权限
                    if ri not in Mine.rights: return u'请联系您的上级领取权限！' #render_template('403.html')

                return func(*args, **kwargs)
            return wrapper
        return decorator


# 直接实例化此类，用于方法的装饰
MineAuthentic = MineAuthentic()

# 系统启动后，只要登录必然触发本文件的程序，以下被触发后会定义新的用户Session机制，用于跨域登录的验证
ErrorCode = {
    401: u'未登录',
    416: u'信息不正确',
    404: u'账户无效',
    403: u'密码错误',
    406: u'被冻结',
    406: u'没有权限',
}

session_key = u'__Mine_%s__' % config.PIM


class MineManager():
    "当前登录账户管理类"
    count = 0  # 定义一个计数器，用于观察类的使用情况
    message = None
    is_online = False
    id = u'-1'
    realname = u'unknown'
    ip = u'0.0.0.0'
    _select = {"passwrd":"", "realname":"", "depart":"", "level":"",  "rights":"", "face":"", "location":"", "status":""}

    def __str__(self):
        return u'%s[%s]' % (self.realname, self.id)

    def __init__(self, request, account=None, passwrd=None, wwx_user=None):
        # __init__() should return None
        self.__class__.count += 1
        if self.__class__.count > 500:
            print('MineManager Class open with %s session.' % self.__class__.count)

        try:
            self.sessionid = session[session_key]
        except:
            self.sessionid = uuid.uuid1()
        if not request:
            return None

        db = SequoiaDB()
        User = wwx_user #？？？以后需要考虑将微信扫码登录集成到本类里
        if wwx_user is None:
            if account is None: return self.__error__(416)
            if passwrd is None: return self.__error__(416)
            passwrd = str(passwrd)

            where = {"account": account, "status": {"$in": (200,206)}}
            orderby = {}
            for q in db.query('users', self._select, where, orderby, limit=1):
                User = q
                break
            if User is None: return self.__error__(404)
            if not (md5(passwrd).hexdigest() == User.passwrd): return self.__error__(403)
        if User.status == 0: return self.__error__(404)  # 暂时设置为不存在，并不提示账户被冻结

        self.id = User.id  # 这里的id是一个24位的字符串
        self.ip = self.get_ipaddress(request)
        self.__load__(User)

        # 存入Session
        if self.message is None:
            self.is_online = True
            self.save()
            # 后记录日志，可以保留下来登录者信息
            User.update({}, request, (1002, u'登录'))

        db.close()

    def __del__(self, ):
        # self.close()
        #不能利用__delete__方法，见close
        self.__class__.count -= 1

    def save(self):
        # 存入Session
        self.timestamp = utils.dt.timestamp()
        sessionid = u'%s@%s' % (session_key, self.sessionid)
        cache.set(sessionid, self, timeout=8 * 60 * 60)
        session[session_key] = self.sessionid
        # print('##### session is save to id [%s].' % sessionid)
        # request.session[session_key] = self

    def close(self, request=None):
        # 释放Session
        # 用户登录时，对象保存到cache中，而页面访问结束后，内存中已经不被引用，故直接被delete掉，执行了本方法清理了cache
        sessionid = '%s@%s' % (session_key, self.sessionid)
        self.sessionid = uuid.uuid1
        cache.delete(sessionid)
        try:
            del session[session_key]
            # del request.session[session_key]
        except:
            pass

    def reload(self, request):
        if not self.is_online:
            return

        db = SequoiaDB()

        Mine = None
        where = {"_id": (self.id,), "status": {"$in": [200, 206]}}
        orderby = {}
        for q in db.query('users', self._select, where, orderby, limit=1):
            Mine = q

            break

        db.close()

        if Mine is None:
            return self.__error__(404)
        if Mine.status == 406:
            return self.__error__(404)  # 暂时设置为不存在，并不提示账户被冻结

        self.id = Mine.id
        self.ip = self.get_ipaddress(request)
        self.__load__(Mine)

        self.save()

    def staff(self):
        #列出下级账户的id
        if self.level == -1:
            pass
        elif self.level == 0:
            return ()
        elif self.level in (1,2,3,4,5):
            db = SequoiaDB()
            child = [self.id]
            _w = {"$or": []} #不考虑状态，避免冻结的账户找不到
            for x in range(0,self.level):
                _w['$or'].append({"leader"+str(x+1): self.id})
            for q in db.query('users', self._select, _w, {}):
                child.append(q.id)
            return tuple(child)

    def __error__(self, code):
        self.message = ErrorCode[code], code

    def __load__(self, Prototype):
        self.realname = Prototype.realname
        self.location = Prototype.location
        self.rights = tuple(Prototype.rights)
        #self.depart = Prototype.depart and Prototype.depart or ""
        self.level = Prototype.level
        self.face = Prototype.face

    def get_ipaddress(self, request):
        # 获取当前用户的IP地址
        return utils.get_ipaddress(request)

    def loclike(self, location=None):
        # 计算需要查询的地区，考虑分公司个别拥有自己的技术团队，所以地区层级查询不同
        if not location: location = ''
        if location == '': location = self.location

        return utils.ft.location(location)


# 扩展WSGIRequest对象，服务进程启动时会执行且仅此一次下面的代码
# Flask支持
from flask import Request as WSGIRequest


def MineManagerRequest(request):
    sessionid = u'#anonymous'
    try:
        sessionid = u'%s@%s' % (session_key, session[session_key])
    except:
        pass
    m = cache.get(sessionid)
    # print('***** cache is read from id [%s].' % sessionid)
    if not m: return MineManager(request)  # 返回Mine实例，以用于未登录时获取当前用户信息，如：IP
    return m


setattr(WSGIRequest, "Mine", MineManagerRequest)
