# coding=utf-8

#db.py v1.2.1 20191113 wht
#last：增加lob对象读写功能，整合添加和修改的验证逻辑 77行

from __future__ import division
from pysequoiadb import client
from pysequoiadb.error import SDBBaseError, SDBEndOfCursor
from bson.objectid import ObjectId
from importlib import import_module
import config, const
import re, math, datetime, time


def strpdate(stime):
    try:
        return datetime.datetime.strptime(stime, '%Y-%m-%d %H:%M:%S')
    except:
        return None


class SequoiaDB(object):
    _ccount = 0  # 定义一个计数器，用于观察类的使用情况
    _client = None
    _utrans = True

    def __init__(self, host=None, port=None, user=None, password=None, name=None, logger=True):
        self.logger = logger
        self.name = name and name or config.database['default']['NAME']
        self.user = user and user or config.database['default']['USER']
        host = host and host or config.database['default']['HOST']
        port = port and port or config.database['default']['PORT']
        password = password and password or config.database['default']['PASSWORD']

        self.__class__._ccount += 1
        if self.__class__._ccount > 100 and self.logger:
            print('Database Class open with %s connection.' % self.__class__._ccount)

        try:
            self._client = client(host, port, self.user, password, ssl=False)
        except SDBBaseError as e:
            raise Exception('The database connection faild. %s' % e)
            del self._client
            exit()

        # 开启数据库事务，利用事务执行所有数据操作，避免程序错误造成的数据调整错位
        if self._utrans: self._client.transaction_begin()

        if self.name[0] == '~':
            self.reportor = True
            self.logger = False
            self.cs = self._client.get_collection_space(self.name)
        else:
            self.reportor = False
            try:
                self.cs = self._client.get_collection_space(self.name + 'data')
            except:
                self.cs = self._client.get_collection_space(self.user)

    def __del__(self, ):
        self.close()
        self.__class__._ccount -= 1

    def close(self):
        if not self._client: return
        self.commit()  # 当数据库对象实例被释放时，先提交事务
        self._client.close_all_cursors()
        self._client.disconnect()
        del self._client

    def commit(self):
        if self._utrans: self._client.transaction_commit()

    def rollback(self):
        if self._utrans: self._client.transaction_rollback()

    def valid(self, cl, k, v, s, data):
        #验证写入的数据是否符合定义的数据模型规则
        # 第2位标记验证方式，已有正则验证、可选值验证，其他可能性需后期增加判断
        try:
            if re.match(s[2], data[k]) is None: v = (k, data[k])
        except:
            if isinstance(s[2], tuple):
                if data[k] not in [i for i, x in s[2]]: v = (k, data[k])

        if isinstance(v, tuple):
            self.rollback()
            raise Exception('The data provided is an exception.(%s: %s)' % v)
        # 更新时只更新设定的内容，所以这里与insert的缩进规则不同
        v = data[k]
        if isinstance(v, dict) and '$stream' in v:
            id, b = (v.get('$id', None), v['$stream'])
            l = len(b) #？？？没有限制数据的大小，Lob数据是较为保密的（如：源码），有必要限制码？
            if id is not None:
                try:
                    cl.remove_lob(id)
                except:
                    id = None
                    #？？？最好在这里做一个警告的记录
            lob = cl.create_lob(id)
            try:
                lob.write(b, l)
            except:
                raise Exception('Failed to write data to lob.(%s: %s)' % (id, l))
            v = lob.get_oid()
            lob.close()
        return v

    def insert(self, request, collection_name, data={}, event_desc=(100, u'写入新数据'), laissez_passer=[]):
        # 每次只能写入一条记录
        if not isinstance(data, dict): return None

        # 这里需要单独写异常处理，避免检查存在性时抛出异常，无法自动创建集合
        try:
            cl = self.cs.get_collection(collection_name)
        except:
            cl = self.create(collection_name)

        if self.reportor:
            record = data
        else:
            record = {}
            try:
                model = import_module('models.%s' % collection_name)
            except:
                self.rollback()
                raise Exception('Model "%s" is not found.' % collection_name)
            for k in model.bson:
                s = model.bson[k]
                # 第0位标记是否索引，第1位标记默认值，只可能是函数、列表/元组、字典、字符和数字，其他可能性需后期增加判断
                try:
                    v = s[1]()
                except:
                    v = s[1]

                if k in laissez_passer: #laissez_passer用于排除 极为特殊极为特殊 的情况，唯一性字段重复时不验证数据的格式是否符合要求
                    v = data[k]
                elif k in data:
                    # 写入信息以结构设置为准，所以data包含未设定的内容时不会被写入
                    v = self.valid(cl, k, v, s, data)
                        
                # 插入时要写入全部数据，所以这里与update的缩进规则不同
                if v is not None: record[k] = v
        try:
            id = str(cl.insert(record))  # 出现“SequoiaDB Error: Failed to insert record”提示时一般都是索引约束
        except SDBBaseError as e:
            self.rollback()
            raise Exception('SequoiaDB Error: Failed to insert record. \r\nDATA: %s' % record)

        log_data = {}
        if self.logger:
            if len(record) > 0: log_data = self.makelog(request, 0, event_desc)
            log_data["pid"] = id
            self.logsave(collection_name, log_data)

        return id

    def change(self, request, collection_name, rules, where={}, event_desc=(100, u'底层方法被执行且为定义描述'), QUERY=None):
        # 更新的主体程序，所有更新都依赖于此程序
        cl = self._collection(collection_name)
        # 1. 校验参数的有效性
        # 必须指定更新的条件，避免批量更新所有数据
        if where is None:
            self.rollback()
            raise Exception('Update must be explicit "where".')
        # 必须设置规则
        if rules is None:
            self.rollback()
            raise Exception('Update must be settings "rules".')

        data = {}

        if self.reportor:
            data = rules
        else:
            try:
                model = import_module('models.%s' % collection_name)
            except:
                self.rollback()
                raise Exception('Model "%s" is not found.' % collection_name)
            record = {}
            for rk in rules:
                data = rules[rk]
                record[rk] = {}
                for k in model.bson:
                    s = model.bson[k]
                    # 第0位标记是否索引，第1位标记默认值，只可能是函数、列表/元组、字典、字符和数字，其他可能性需后期增加判断
                    try:
                        v = s[1]()
                    except:
                        v = s[1]

                    if k in data:
                        # 写入信息以结构设置为准，所以data包含未设定的内容时不会被写入
                        v = self.valid(cl, k, v, s, data)
                        # 更新时要写入的是部分数据，所以这里与insert的缩进规则不同
                        if v is not None: record[rk][k] = v
                        # 同步更新Q实例的数据
                        if QUERY:
                            setattr(QUERY, k, v)
                            QUERY.serializer[k] = v

        try:
            cl.update(record, condition=where, hint={})
        except:
            self.rollback()
            raise Exception('Modify data execute faild. %s, %s' % (rules, where))

        log_data = {}
        if self.logger:
            if QUERY:
                logpid = QUERY.id
            else:
                logpid = 0
                event_desc = list(event_desc)
                event_desc[1] = u'【查询外的批量处理】w:(%s)。%s' % (where, event_desc[1])
            log_data = self.makelog(request, logpid, event_desc)
        if self.logger: self.logsave(collection_name, log_data)

    def filterwhere(self, where):
        w = {}
        for k, v in where.items():
            if k in ('_id','-id'):  # 根据_id进行查询时，必须是元组；_id表示等于，-id表示排除
                if not isinstance(v, tuple):
                    self.rollback()
                    raise Exception('Field "_id" must be tuple!')
                id = []
                for x in v:
                    id.append(ObjectId(x))
                if not "_id" in w: w["_id"] = {}
                if   k == "_id": w["_id"]["$in"] = id
                elif k == "-id": w["_id"]["$nin"] = id
            elif isinstance(v, dict) and '$date' in v:
                vset = v.get('$date', (None, None))
                if not isinstance(vset, tuple):
                    self.rollback()
                    raise Exception('Query set "$data" must be tuple!')
                stime = strpdate(vset[0])
                etime = strpdate(vset[1])
                w[k] = {"$isnull": 0}
                if stime: w[k]["$gte"] = stime
                if etime: w[k]["$lte"] = etime
            else:
                w[k] = v

        return w

    def count(self, collection_name, where=None):
        cl = self._collection(collection_name)
        where = self.filterwhere(where)
        return cl.get_count(condition=where)

    def query(self, collection_name, select, where={}, order_by={}, limit=100000, skip=0):
        # 标准查询
        # limit：查询条数，skip：从哪条开始（第1条为0）
        # 这里需要单独写异常处理，避免检查存在性时抛出异常，无法自动创建集合
        try:
            cl = self._collection(collection_name)
        except:
            cl = self.create(collection_name)

        selector = {} #防止传入的select参数被方法修改
        if not select.get("*", False):
            selector["_id"] = u''
            for k,v in select.items():
                selector[k] = v

        where = self.filterwhere(where)

        # 数据结构定义中可以定义记录可用的数据方法（自动引入记录实例self，不能有其他参数），从Q继承
        if self.reportor:
            model = ''
        else:
            model = import_module('models.%s' % collection_name)
        _Q = hasattr(model, 'func') and getattr(model, 'func') or self.Q

        query = []
        eof = False
        '''
        用于分组
        s = {}
        for k,v in selector.items():
            s[k] = 1
        option = [
            {"$project": s},
            {"$match":   where},
            {"$limit":   long(limit)},
            {"$skip":    long(skip)},
            {"$sort":    order_by}
        ]
        #cursor = cl.aggregate(option)
        '''
        cursor = cl.query(condition=where, selector=selector, order_by=order_by, hint={}, num_to_skip=long(skip),
                          num_to_return=long(limit))
        while True:
            q = None
            try:
                q = cursor.next()
            except SDBEndOfCursor as e:
                break
            # 把获取到的数据写入到一个待返回的列表变量，不写入到字典的原因是字典会自动改变顺序
            if q: query.append(_Q(q, cl, self))

        return query

    def aggregate(self, collection_name, group, where={}):
        #聚合查询
        #collection_name: 集合名
        #where: 字典类型，需要聚合查询的数据条件
        #group: 字典类型，需要聚合的字段
        if not (collection_name and isinstance(collection_name, str)):
            raise ValueError('Do not find collection name!')
        if not isinstance(where, dict):
            raise ValueError('match must be dict')
        if not (group and isinstance(group, dict)):
            raise ValueError('group must be dict')


        param = [{"$match": where}, {"$group": group}]
        cursor = self.cs.get_collection(collection_name).aggregate(param)
        cl = self._collection(collection_name)
        _Q = self.Q
        query = []
        while True:
            q = None
            try:
                q = cursor.next()
            except SDBEndOfCursor as e:
                break
            #把获取到的数据写入到一个待返回的列表变量，不写入到字典的原因是字典会自动改变顺序
            if q:
                query.append(_Q(q, cl, self))
        return query


    def pagebar(self, collection_name, select, where, order_by, args, page=[20, 1]):
        # 翻页查询
        # page_set：一个2位的数组，第一位表示一页显示的条数，第二位表示当前页
        page_size = int(page[0])
        page_numb = int(page[1])

        count = self.count(collection_name, where)
        page_cont = int(math.ceil(count / page[0]))
        if page_cont == 0: page_cont = 1
        if page_numb > page_cont: page_numb = page_cont
        page_star = page_size * (page_numb - 1)

        query = self.query(collection_name, select, where, order_by, page_size, page_star)
        return self.P(query, (count, page_cont, page_numb), args)

    def makelog(self, request, pid, event_desc):
        ltype = event_desc[0]
        ldesc = event_desc[1]
        if ltype not in const.EVENT_TYPE:
            self.rollback()
            raise Exception('Operation for database with type is undefined.')

        Mine = request.Mine()
        operater = '%s' % Mine
        ipaddres = Mine.get_ipaddress(request)

        return {
            "ts":  time.time(),
            "lt":  ltype,
            "ld":  ldesc,
            "pid": pid,
            "op":  operater,
            "ip":  ipaddres,
        }

    def logsave(self, collection_name, data):
        log_collection = '~%s' % collection_name
        log_data = data

        try:
            lcs = self._client.get_collection_space(self.name + 'log')
        except:
            lcs = self._client.get_collection_space(self.user)
        # 这里需要单独写异常处理，避免检查存在性时抛出异常，无法自动创建集合
        try:
            cl = lcs.get_collection(log_collection)
        except:
            cl = lcs.create_collection(log_collection)

        cl.insert(log_data)

    def _collection(self, collection_name):
        try:
            return self.cs.get_collection(collection_name)
        except:
            self.rollback()
            raise Exception('Collection "%s" is not already.' % collection_name)

    def hascl(self, collection_name):
        try:
            cl = self.cs.get_collection(collection_name)
            return True
        except:
            return False

    def create(self, collection_name):
        # 集合模型格式
        """
        file model_name:
            bson = {
                "字段名1":(<是否唯一，0:否，不唯一; 1:是，信息唯一;>,<默认值>,<赋值范围>,<字段说明>),
                "字段名2":(<是否唯一，0:否，不唯一; 1:是，信息唯一;>,<默认值>,<赋值范围>,<字段说明>),
                **特别说明：
                    1. 默认值是
                    a)函数定义时，表示执行函数取得赋值，
                    b)其他类型时，直接赋值。
                    2. 赋值范围是
                    a)函数定义时，表示执行函数取得赋值，原始赋值作为参数，
                    b)字符串时，表示正则表达式校对，
                    c)列表（或元组、字典）时，表示限定赋值范围，
                    d)空字符串或None时，表示没有限制。
            }
            index = {
                "索引名称":{
                    '字段名1':<索引规则1，-1：asc；1：desc；>,
                    '字段名2':<索引规则2，-1：asc；1：desc；>
                },
            }
            default = (<创建时，默认需要写入的数据>
                {
                    "字段名1":"值1",
                    "字段名2":"值2",
                },
            )
        """
        # 这里需要单独写异常处理，避免检查存在性时抛出异常，无法自动创建集合
        try:
            self.cs.get_collection(collection_name)
            self.rollback()
            raise Exception('Collection "%s" is already.' % collection_name)
        except:
            pass
        # 当insert数据时，如果还没有创建集合，则自动创建，但所有的集合都需要预先定义，避免程序bug而产生的垃圾集合
        # 集合定义都保存在models目录里，通过动态model获取机制取得定义设置
        if not self.reportor: model = import_module('models.%s' % collection_name)

        # 开始创建集合并建立唯一性索引
        cl = self.cs.create_collection(collection_name)
        if self.reportor: return cl
        for k in model.bson:
            v = model.bson[k]
            if v[0] == 1:
                cl.create_index({k: -1}, u'UNIQUE_%s_%s' % (collection_name.upper(), k.upper()), True, True)
        # 创建集合索引
        [cl.create_index(model.index[k], u'IX_%s_%s' % (collection_name.upper(), k.upper()), False, False) for k in
         model.index]
        # 写入默认的初始化数据
        if hasattr(model, 'default'): [cl.insert(x) for x in model.default]

        try:
            tcl = self.cs.get_collection('@tables')
        except:
            tcl = self.cs.create_collection('@tables')
        tcl.insert({"name": collection_name, "dt": datetime.datetime.now()})

        return cl

    class Q():
        # 类的内置类，用于生成行记录的对象
        def __init__(self, cursor, collection, db):
            self.db = db
            self.collection = collection
            self.serializer = {}
            for k in cursor.keys():
                if k == '_id':
                    setattr(self, 'oid', cursor[k])
                    setattr(self, 'id', str(cursor[k]))
                    self.serializer['id'] = str(cursor[k])
                else:
                    setattr(self, k, cursor[k])
                    self.serializer[k] = cursor[k]

        def __str__(self):
            return str(self.serializer)

        def update(self, data, request, event_desc=(100, u'更新对象数据')):
            rules = {"$set": data}
            self.db.change(request, self.collection.get_collection_name(), rules, {"_id": self.oid}, event_desc, self)

        def insert(self, data, request, event_desc=(100, u'补充字符数据')):
            rules = {"$inc": data}
            self.db.change(request, self.collection.get_collection_name(), rules, {"_id": self.oid}, event_desc, self)

        def pushed(self, data, request, event_desc=(100, u'数据写入到子集')):
            rules = {"$push": data}
            self.db.change(request, self.collection.get_collection_name(), rules, {"_id": self.oid}, event_desc, self)

        def delete(self, request, event_desc=(100, u'删除对象（逻辑）')):
            # 只做逻辑删除，仅在极为特殊的情况才利用remove方法进行物理删除，为了保护信息物理删除由运维操作
            rules = {"$set": {"status": 0}}
            self.db.change(request, self.collection.get_collection_name(), rules, {"_id": self.oid}, event_desc, self)

        def remove(self, request, event_desc=(100, u'删除对象（物理）')):
            # 抛出异常，避免程序漏洞误删除
            if not (event_desc[0] == 999):
                self.db.rollback()
                raise Exception('Please set log description!')
            self.collection.delete(condition={'_id': self.oid}, hint={})
            # 物理删除必须记录日志
            log_data = self.db.makelog(request, self.id, event_desc)
            self.db.logsave(self.collection.get_collection_name(), log_data)

        def read(self, key):
            #读取一个LOB对象
            if key is None: raise Exception('Property key has no assignment.')
            id = getattr(self, key)
            lob = self.collection.get_lob(id)
            length = lob.get_size()
            stream = lob.read(length)
            lob.close()
            return stream

        def clear(self, key):
            #删除一个LOB对象
            if key is None: raise Exception('Property key has no assignment!')
            id = getattr(self, key)
            try:
                self.collection.remove_lob(id)
            except:
                pass #？？？最好在这里做一个警告的记录

    class P():
        # 类的内置类，用于生成翻页工具的对象
        def __init__(self, data, page, args):
            self.data = data
            self.size = page[0]  # size[0]：数据记录总数
            self.page = page[2]  # size[2]：当前页码
            self.bar = self.__bar__(args, page[1])  # size[1]：分页总页数

        def __bar__(self, args, s):
            if s == 1: return u''
            siz = s
            cur = self.page
            pre = cur > 1 and cur - 1 or 1
            nxt = cur < s and cur + 1 or s
            arg = u''
            for k, v in args.items():
                if v <> '': arg += u'&%s=%s' % (k, v)
            lr = 3

            html = u'<div class="pagebar">'
            if cur > 1: html += u'<a href="?p=%(pre)d%(arg)s" title="上一页">&lt;&lt;</a>&nbsp;&nbsp;<a href="?p=1%(arg)s">1</a>&nbsp;&nbsp;'
            if cur - lr > 2: html += u'<span>...</span>&nbsp;&nbsp;'
            if cur > 2:
                for x in range(cur - 3, cur):
                    if x > 1: html += u'<a href="?p=%(pag)d%(arg)s">%(pag)d</a>&nbsp;&nbsp;' % {'pag': x, 'arg': arg}
            html += u'<span class="ac">%(cur)d</span>&nbsp;&nbsp;'
            if cur < s - 1:
                for x in range(cur + 1, cur + 4):
                    if x >= s: break
                    html += u'<a href="?p=%(pag)d%(arg)s">%(pag)d</a>&nbsp;&nbsp;' % {'pag': x, 'arg': arg}
            if cur + lr < s - 1: html += u'<span>...</span>&nbsp;&nbsp;'
            if cur < s: html += u'<a href="?p=%(siz)d%(arg)s">%(siz)d</a>&nbsp;&nbsp;<a href="?p=%(nxt)d%(arg)s" title="下一页">&gt;&gt;</a>&nbsp;&nbsp;'
            html += u'<b>找到 %s 项</b></div>' % (self.size)

            return html % {
                'arg': arg,
                'cur': cur,
                'pre': pre,
                'nxt': nxt,
                'siz': siz,
            }


class MySQLDB(object):
    # 历史代码开始，SequoiaDB同样支持SQL查询，以后可以扩展
    def sqlexec(self, sqlstr):
        self.cursor.exec_sql(sqlstr, None)
        scmd = sqlstr[:6]
        if scmd.lower() == 'select':
            qury = self.cursor.fetchall()
            desc = self.cursor.description
            return (qury, [dict(zip([c[0] for c in desc], r)) for r in qury])
        else:
            return (0, 1)
            # 历史代码结束，SequoiaDB同样支持SQL查询，以后可以扩展


class _DBUtils():
    def erpid2customer(self, conn, erpid, name, select):
        # 找出客户并验证企业名称是否存在重复
        # 客户重复，以客户企业名称为准，主程序更新日志并记录多余的erpid
        if not conn.hascl('customer'): return (None, name, ())

        s = select
        s["erpid"] = ""
        s["name"] = ""
        w = {"name": {"$et": name}}
        for q in conn.query('customer', s, w, {}):
            if q.erpid <> erpid:
                return (q, q.name, (q.erpid,))
            else:
                return (q, q.name, ())
        return (None, name, ())

    def carid2maker(self, conn, *args, **kwargs):
        # 根据身份证号码找出用户基本信息
        id = None
        name = None
        grp = None
        if not conn.hascl('users'): return (id, name, grp)
        select = {"uuid": "", "realname": "", "depart": ""}
        where = kwargs
        where["status"] = {"$in": [200, 206]}
        querys = conn.query('users', select, where, {}, limit=1)
        for q in querys:
            id = q.id
            name = q.realname
            grp = q.depart
            break
        return (id, name, grp)


dbutils = _DBUtils()