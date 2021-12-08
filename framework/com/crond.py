# coding=utf-8
from multiprocessing import Process
from hashlib import md5
import os, time, datetime

class BaseMonitor():
    def __init__(self):
        pass

    def process(self, *args, **kwargs):
        u"用于需要持续执行的过程，如：监控Monitor"

    def run(self):
        k = Process(target=self.process)
        k.daemon = True
        k.start()

class Object(): pass
class BaseReport():
    depict = '默认报表'

    def __init__(self):
        self.object = Object

    def statistic(self, *args, **kwargs):
        u"统计算法的实现，用于特定统计需求的数据汇总和报表制作"

    def process(self, *args, **kwargs):
        u"用于需要持续执行的过程，如：监控Monitor"

    def jsonfromdb(self, *args, **kwargs):
        u"统计结果的查询和输出，一般来源于界面的ajax请求"

    def exe(self):
        if self.islock(): return
        self.lock()
        self.statistic()

    def run(self):
        if self.islock(): return
        self.lock()
        k = Process(target=self.statistic)
        k.daemon = True
        k.start()

    def cachefile(self):
        p = '%s/cache/lock' % '/'.join([d for d in os.path.abspath(__file__).split('/')][:-3])
        if not os.path.exists(p): os.makedirs(p)
        return '%s/%s' % (p, md5(self.depict).hexdigest())

    def islock(self):
        #用于锁定更新过程
        if os.path.exists(self.cachefile()):
            return True
        return False

    def lock(self):
        #用于锁定更新过程
        open(self.cachefile(), 'a+').write(datetime.datetime.now().strftime('%d,%H:%M:%S'))

    def unlock(self):
        #用于锁定更新过程
        os.remove(self.cachefile())

    def ver(self, time_struct=None):
        if time_struct is None: time_struct = time.localtime()
        dt = time.strftime('%Y%m00', time_struct)
        yy = dt[:4]
        mm = dt[4:6]
        dd = dt[6:8]
        result = u'%s_%s%s%s' % (u'%s', yy, mm, dd)
        if   mm == '00':
            result = u'%s_%s' % (u'%s', yy)
            mm = '01'
            dd = '01'
        elif dd == '00':
            result = u'%s_%s%s' % (u'%s', yy, mm)
            dd = '01'
        else:
            result = u'%s_%s%s%s' % (u'%s', yy, mm, dd)
        return (result % self.depict.decode('utf8'), yy, mm, dd)
