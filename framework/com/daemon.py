# coding=utf-8
import time
import atexit, os, sys, signal
import traceback
import config

class Daemon(object):
    #守护进程类，用于启动一个守护进程进行监控、自动任务等
    pid = None
    ppid = None

    def __init__(self, name, homedir='.', stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, umask=022):
        if not name: raise Exception('Must be given a name.\n')
        self.name = name

        path = homedir
        if path.find("/") > -1:
            path = homedir.split('/')[:-1]
            path.append('_daemon/null')
            path = os.path.dirname('/'.join(path))
        if not os.path.exists(os.path.join(path, 'wait')): os.makedirs(os.path.join(path, 'wait'))
        if not os.path.exists(os.path.join(path, 'done')): os.makedirs(os.path.join(path, 'done'))
        #os.system('chmod -R 660 %s' % path)

        self.homedir = path.lower()
        self.stdin   = stdin
        self.stdout  = '%s/%s.log' % (self.homedir, self.name.lower())
        self.stderr  = '%s/%s.log' % (self.homedir, self.name.lower())
        self.verbose = config.debug and 1 or 0 #调试开关
        self.umask   = umask
        self.alive   = True
        self.pidfile = '%s/pid.%s' % (self.homedir, self.name.lower())

    def daemonize(self):
        if self.verbose >= 1: sys.stdout.write('[%s]Current process start forking ......\n' % os.getpid())
        #sys.stdout.writelines((os.getenv(), '\n'))

        ppid = os.getpid()

        try:
            pid = os.fork()
            if pid > 0: #current process is parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir(self.homedir)
        os.setsid()
        os.umask(self.umask)
        
        if self.verbose >= 1: sys.stdout.write('[%s]Daemon process start forking ......\n' % os.getpid())

        try:
            pid = os.fork()
            if pid > 0: #current process is parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = so

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        def handler(signum, frame):
            self.alive = False
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)

        #atexit.register(self.exit)
        sys.exitfunc = self.exit

        self.setpid(os.getpid(), ppid)

        if self.verbose >= 1: sys.stdout.write('[%s]Daemon process is running.\n' % os.getpid())

    def start(self, *args, **kwargs):
        if self.verbose >= 1: sys.stdout.write('[%s]Starting %s ......\n' % (os.getpid(), self.name))
        if os.path.exists(self.pidfile):
            f = open(self.pidfile, 'r')
            pid = f.read()
            f.close()
            if pid == os.getpid():
                sys.stderr.write('[%s]Process is started.\n' % pid)
                return
            #self.stop(pid=pid)
            #？？？应该先判断进程是否还活着，如果活着就不动，如果死了就启动
            return
            
        self.daemonize()
        pid = self.getpid()
        if pid:
            f = open(self.pidfile, 'a')
            f.write(str(pid))
            f.close()
            if os.getpid() == pid:
                sys.stderr.write('[%s]Process is running.\n' % pid)
                self.run(*args, **kwargs)
        else:
            sys.stderr.write('[%s]Daemon is stopping.\n' % pid)

    def stop(self, pid=None):
        if self.verbose >= 1: sys.stdout.write('Stopping %s ......\n' % self.name)
        pid = pid and pid or self.getpid()
        if not pid:
            sys.stderr.write('Daemon process [%s] exited.\n' % pid)
            return
        #try to kill the daemon process
        try:
            i = 0
            while 1:
                sys.stderr.write('kill:(%s)ppid[%s] -- pid[%s] -- ospid[%s] -- alive:%s\n' % (i, self.__class__.ppid, pid, os.getpid(), str(self.alive)))
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                #if i % 10 == 0: os.kill(pid, signal.SIGHUP)
                if i % 100 == 0: sys.exit(1)
                #if i % 99 == 0: os.kill(pid, signal.SIGKILL)
        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                self.exit()
            else:
                sys.exit(1)
            if self.verbose >= 1: sys.stdout.write('[%s]Process [%s] is stoped.\n' % (pid, self.name))

    def getprocess(self, pid):
        #获取某个进程
        pass

    def running(self):
        #返回当前守护进程的状态
        p = self.getprocess(self.getpid())
        return p.alive

    def run(self, *args, **kwargs):
        'NOTE: override the method in subclass'
        pass

    def exit(self):
        if os.path.exists(self.pidfile): os.remove(self.pidfile)

    def getpid(self):
        return self.__class__.pid

    def setpid(self, pid, ppid):
        self.__class__.pid = pid
        self.__class__.ppid = ppid

    def keepon(self):
        #用于字典式判断的默认方法，可以让程序继续执行
        pass


import socket, shutil
from multiprocessing import Process
from importlib import import_module

class Monitor(Daemon):
    #监控类，用于执行和管理需要守护模式下进行的任务
    #？？？怎么判断这个类只被app的启动所调用？
    jobs = {} #用于记录正在执行的任务
    sock = u'./monitor.sock'
    def __init__(self, name, _file='.'):
        self.name = name
        Daemon.__init__(self, name, homedir=_file)
        self.sock = '%s/%s.sock' % (self.homedir, name.lower())

    def reboot(self, *args, **kwargs):
        self.stop()
        self.start(*args, **kwargs)

    def powoff(self, *args, **kwargs):
        self.stop()

    def startup(self, stampid, instance):
        wrkpath = os.path.join(self.homedir, 'wait', stampid)

        stdout = open(os.path.join(wrkpath, 'run'), 'w')
        stdout.write("Task [%s] is startup...\n" % stampid)
        try:
            instance(stdout)
        except:
            stdout.write("Task [%s] failed.\n" % stampid)
            traceback.print_exc(file=stdout)
            stdout.close()
            shutil.move(wrkpath, os.path.join(self.homedir, 'done', '0e%s' % stampid))
            time.sleep(20)
            sys.exit(0)

        #执行完毕以后，将wait目录下的任务文件移动到done里
        shutil.move(wrkpath, os.path.join(self.homedir, 'done', stampid))
        stdout.write("Task [%s] is finished.\n" % stampid)
        #*************************调试方法
        #stdout.write(str(self.__class__.jobs))
        #stdout.write(stampid)
        #p = self.__class__.jobs.get(stampid, None)
        #if p: p.join()
        #self.__class__.jobs.pop(stampid)
        #stdout.write(str(self.__class__.jobs))
        #*************************调试方法
        stdout.close()
        sys.exit(0)

    def run(self, *args, **kwargs):
        path = os.path.join(self.homedir, 'wait')
        while self.alive:
            for folder in os.listdir(path):
                wrkpath = os.path.join(path, folder)
                cmdfile = os.path.join(wrkpath, 'cmd')
                runfile = os.path.join(wrkpath, 'run')
                if not os.path.isdir(wrkpath): continue #只找出目录，任务命令（cmd）保存在以时间戳命名的目录里
                if not os.path.exists(cmdfile):
                    #如果命令文件不存在，则删除目录并退出
                    shutil.rmtree(wrkpath)
                    continue
                if os.path.exists(runfile): continue #执行文件（run）存在，表示正在执行，或执行被强制终止
                cmd = None
                try:
                    #先生成执行文件（run），表示已经开始执行，避免其他进程对其操作，造成重复执行
                    open(runfile, 'a').close()
                    #读取命令
                    f = open(cmdfile, 'r')
                    cmd = f.read()
                    f.close()
                except:
                    shutil.move(wrkpath, os.path.join(self.homedir, 'done', '0e%s' % folder))
                    continue
                cmd = cmd.strip().replace('\r','').replace('\n','')
                define = {
                    u'powoff': self.powoff,
                    u'reboot': self.reboot
                }
                if cmd in define: define[cmd]()

                instance = None
                if cmd:
                    cls = cmd[25:]
                    oid = cmd[:24]
                    try:
                        c = import_module(cls)
                        instance = c(oid)
                    except:
                        sys.stderr.write('Task [%s] class is not defined.\n' % folder)

                if not hasattr(instance, '__call__'):
                    sys.stderr.write('Task [%s] class no method <start>.\n' % folder)
                    shutil.move(wrkpath, os.path.join(self.homedir, 'done', '0e%s' % folder))
                    continue
                p = Process(name='%s-%s' % (self.name, folder), target=self.startup, args=(folder, instance,))
                p.daemon = True
                #self.__class__.jobs[folder] = p
                p.start()
                time.sleep(1)
            time.sleep(3) #需要停顿3秒，避免冲突处理

def MonitorStart(name, abspath):
    file = '%s/daemon/%s.py' % (abspath, name.lower())
    f = open(file, 'a')
    f.write("""#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
import sys,os
sys.path.append('%s/framework')
from com.daemon import Monitor
if __name__ == '__main__':
    Monitor('%s', _file='%s').start()
""" % (abspath, name, abspath))
    f.close()
    
    os.system('python %s' % file)
