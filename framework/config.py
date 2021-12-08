#-*- coding:utf-8 -*-
debug = True

PIM = u'tsp-beta'
storage = u'/home/stores/beta' #末尾不能有"/"

database = {
    'default': {
        'ENGINE': 'pysequoiadb', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bop',           # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '218.60.0.211',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '11810',         # Set to empty string for default.
    },
    # 'default': {
    #         'ENGINE': 'pysequoiadb',
    #         'NAME': 'tsp',
    #         'USER': 'pvsap',
    #         'PASSWORD': 'k2s9k3u9r6',
    #         'HOST': '218.60.0.211',
    #         'PORT': '31611',
    #     }
}

#cache = ('werkzeug.contrib.cache.MemcachedCache', '10.1.0.91:11211', 9000)
cache = ('werkzeug.contrib.cache.MemcachedCache', 'localhost:11211', 9000)
#'default': { 
#    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#    'LOCATION': 'cache.duapp.com:20243',
#    'TIMEOUT':  9000,
#}

credible = {
    u'erp@211.137.44.166' : u'hQXFznK50dyoNDAL',
    u'erp@218.24.104.62'  : u'hQXFznK50dyoNDAL',
    u'erp@175.19.185.150' : u'hQXFznK50dyoNDAL',
    u'erp@121.28.6.2'     : u'hQXFznK50dyoNDAL',
    u'erp@222.223.250.210': u'hQXFznK50dyoNDAL',
    u'erp@10.2.2.10'     : u'hQXFznK50dyoNDAL',
}

wechat = {
    u'CORPID': 'wwe6a967e2bfd97adf',
    u'CORPSECRET': 'VGDa3rrZVT0wk06S1JZBlwGVoX3XRdEBZKjmaqvpfj8'
}

#百度用户名必须是字符串不可以是unicode编码
baiduagent = (
    (u'erpdb', 'ak', 'sk')
)
#万网用户名必须全是数字
aliagent = (
    (u'erpdb', u'user|pwd|中国万网|admin@panguweb.cn|')
)