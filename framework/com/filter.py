# coding=utf-8
#template filter
#过滤器不应该有数据查询过程，以规避数据循环造成的性能问题
import locale, time
import choices

def dateformat(value, format='%Y-%m-%d %H:%M:%S'):
    #|dateformat('%Y-%m-%d %H:%M:%S')
    try:
        return time.strftime(format, time.strptime(str(value), '%Y-%m-%d %H:%M:%S'))
    except:
        try:
            return time.strftime(format, time.strptime(str(value), '%Y-%m-%d %H:%M:%S.%f'))
        except:
            return value and value or u''

def gender(value):
    #|gender
    v = {
        u'1': u'男',
        u'2': u'女',
    }
    
    return v.get(str(value), value)

def realname(value):
    #|realname
    v = value
    if u'[' in v:
        v = v[:v.find(u'[')]
    
    return v

def checked(val, cal):
    #|checked(number)
    if not isinstance(val, list): return u''
    if cal in val: return u' checked'
    #不在考虑位运算的方式，非关系型数据库最大的优势就是数据的直接应用，避免页面渲染时的大量运算，再使用位运算效率会更低。wht 20191017
    return u''

def selected(val, cal, ply=u' selected="selected"'):
    #|selected(number)
    if val == cal: return ply
    return u''

def label(value, size):
    #|label(size)
    if not isinstance(value, list): return u'？！'
    v = u''
    i = 0
    for x in value:
        i = i + 1
        v = u'%s %s' % (v, x)
        if i == size:
            v = u'%s...' % v
            break
        else:
            v = u'%s;' % v
    
    return v

def choice(val, param):
    d = getattr(choices, param, None)
    if d:
        d = dict(d)
        return d.get(val, u'')
    return val

def money(val):
    locale.setlocale(locale.LC_ALL, '') # Set the locale for your system
    return locale.format("%.2f", val, 1)
def ratio(val, mode=1):
    method = {
        1: lambda x: u'{:.2%}'.format(x),
        2: lambda x: u'%s折' % u'{:.2f}'.format(x*10)[:4],
    }
    if not mode in method: return val
    return method[mode](val)

#过滤器初始化方法，始终在此文件代码的最后，且仅被app调用
def initialize(app):
    app.jinja_env.filters['dateformat'] = dateformat
    app.jinja_env.filters['gender']     = gender
    app.jinja_env.filters['realname']   = realname
    app.jinja_env.filters['checked']    = checked
    app.jinja_env.filters['selected']   = selected
    app.jinja_env.filters['label']      = label
    app.jinja_env.filters['choice']     = choice
    app.jinja_env.filters['money']      = money
    app.jinja_env.filters['ratio']      = ratio
