# coding=utf-8

#sf.py v1.0.3 20191114 wht
#last：独立文件后缀的获取方法，限制文件上传大小 26行 36行

import os, shutil, time
import config
class StreamFileLocal():
    #每个实例只管理一个文件
    allow = {
        'FFD8FF':'jpg', '474946':'gif', '000001':'mpg', '415649':'avi', '3C3F78':'xml',
        '89504E':'png', '060500':'raw', '424D3E':'bmp', '00FFFF':'img', '49492A':'tif', 
        '255044':'pdf', 'D0CF11':'ppt', '526172':'rar', '384250':'psd', '504B':'zip', 
    }
    stream = None #文件的流数据
    live = None #文件的真实存储路径
    name = u'' #文件名
    def __init__(self, data, root=None, req=None):
        self.root = root is None and '/'.join([d for d in os.path.abspath(__file__).split('/')][:-3]) or root
        #定义一个缓存目录，用于临时存放上传的文件，待正式提交数据时处理文件并移动到正式可访问的目录下
        self.cache = '%s/cache/_file' % self.root
        #读取文件的内容流数据（$stream)或准备操作的文件地址($file)
        if not isinstance(data, dict): raise Exception('File data format is faild!')
        #？？？如何判断数据是否是流数据？
        if "$stream" in data:
            self.stream = data["$stream"]
        if "$file" in data:
            arr = data["$file"].split('/')
            self.live = '/'.join(arr[:-1])
            #if self.live == u'': self.live = self.cache #？？？可能有问题，只提交一个文件名，且文件在根下
            self.name = arr[-1]

    def __build(self, name, path='/'):
        #path必须是以“/”开头和结尾的
        if not os.path.exists(path): os.makedirs(path)
        return '%s%s' % (path, name)

    def __fix(self, filepath):
        f = open(filepath, 'rb')
        s = f.read(5)
        f.close()
        hd = ''.join([('00%s' % hex(ord(b)).replace('0x','').upper())[-2:] for b in s])
        h4, h6 = hd[:4], hd[:6]
        fix = self.allow.get(h6, self.allow.get(h4, 'tmp'))
        if fix == 'tmp':
            f = open('%s/headerflag' % self.root, 'a')
            f.write(u'%s    %s\r\n' % (hd, filepath))
            f.close()
        return fix

    def save(self, limit=10):
        #文件写入到缓存目录中
        if self.stream is None: raise Exception('No stream data request!')
        if len(self.stream) > limit * 1024 * 1024: return 206 #大小限制，默认10M
        name = '%s%s' % (time.strftime('%y%m',time.localtime()), str(int(time.time() * 1000000))[7:])
        c = self.__build(name, '%s/' % self.cache)
        f = open(c, 'wb')
        f.write(self.stream)
        f.close()
        self.live = c
        self.name = name
        return self

    def storage(self, cls='0', customize=None):
        #文件移动到存储仓库目录中
        #   dest：自定义存储目标
        #   cmiz：自定义文件名
        c = self.__build(self.name, '%s/' % self.cache)
        suffix = self.__fix(c)
        if customize is None:
            filepath = '%s/%s/%s' % (config.storage, self.name[:4], self.name[4:6])
            filename = '%s%s.%s' % (cls, self.name[6:], suffix)
        else:
            arr = customize.split('/')
            filepath = '%s/%s' % (config.storage, '/'.join(arr[:-1]))
            filename = '%s.%s' % (arr[-1], suffix)
        p = self.__build(filename, filepath)
        shutil.move(c, p)
        depth = len(config.storage.split('/'))
        self.live = filepath
        self.name = '/'.join([d for d in p.split('/')][depth:])
        return self

    def read(self):
        #读取文件流数据，读文件说明文件一定存在，但由于逻辑问题，可能上传后的package数据只有临时文件名，没有路径
        p = '%s/%s%s' % (self.root, self.live, self.name)
        if not self.exist((p,)) == u'':
            p = '%s/%s' % (self.cache, self.name)
        f = open(p, 'rb')
        self.stream = f.read()
        f.close()
        return self.stream

    def remove(self):
        #删除文件
        f = '%s/%s/%s' % (self.root, self.live, self.name)
        if os.path.isfile(f): os.remove(f)

    def exist(self, files, root=None):
        #验证文件是否存在的方法，返回丢失的文件
        #files 数组，可以同时验证多个文件
        #root 表示需要从哪个目录里找这个文件，为None时代表从config.storage里找
        if root is None: root = config.storage
        for f in files:
            c = '%s/%s' % (root, f)
            if not os.path.isfile(c):
                return f
        return u''

"""
000001	mpa
000002	tga
000002	tag
000007	pjt
00000F	mov
000077	mov
000100	ddb
000100	ttf
000100	tst
005001	xmv
00FFFF	mdf
00FFFF	smd
0A0501	pcs
17A150	pcb
1F9D8C	z
202020	bas
234445	prg
234558	m3u
24536F	pll
2A2420	lib
2A5052	eco
2A7665	sch
2E524D	rm 
3026B2	wmv
3026B2	wma
31BE00	wri
3C2144	htm
3C3F78	xml
3C3F78	msc
3F5F03	hlp
3F5F03	lhp
414331	dwg
42494C	ldb
434841	fnt
435753	swf
484802	pdg
495363	cab
495453	chm
4C0000	lnk
4D4544	mds
4D5A16	drv
4D5A50	dpl
4D5A90	exe
4D5A90	dll
4D5A90	ocx
4D5A90	olb
4D5A90	imm
4D5A90	ime
4D5AEE	com
4E4553	nes
524946	wav
526172	rar
526563	eml
526563	ppc
584245	xbe
5B4144	pbk
5B436C	ccd
5B5769	cpx
60EA27	arj
7B5072	gtd
7B5C72	rtf
805343	scm
87F53E	gbc
C22020	nls
C5D0D3	eps
D0CF11	xls
D0CF11	max
E93B03	com
FFFB50	mp3
FFFE3C	xsl
FFFFFF	sub
"""