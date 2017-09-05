from utils import log
from models.user import User
from models.message import Message


# 读出相关的数据
def template(name):
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')

    r = header + '\r\n' + body

    return r.encode()


def route_login(request):
    # 登陆的路由函数
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'

    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''
    body = template('login.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body

    return r.encode()


def route_register(request):
    # 注册的路由函数
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'

    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body

    return r.encode()


def route_message(request):
    """
    message页面的处理函数, 返回对应的响应
    """
    form = request.query

    if len(form) > 0:
        m = Message.new(form)
        log('get', form)
        m.save()
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('html_basic.html')
    ms = '<br>'.join([str(m) for m in Message.all()])
    body = body.replace('{{messages}}', ms)
    r = header + '\r\n' + body

    return r.encode(encoding='utf-8')


def route_message_add(request):
    """
    处理增加信息的路由函数
    """
    form = request.form()
    m = Message.new(form)
    m.save()

    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('html_basic.html')
    ms = '<br>'.join([str(m) for m in Message.all()])

    body = body.replace('{{messages}}', ms)
    r = header + '\r\n' + body

    return r.encode(encoding='utf-8')


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename = request.query.get('file', 'doge.gif')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        r = header + b'\r\n' + f.read()
        return r


def route_dict():
    d = {
        '/': route_index,
        '/login': route_login,
        '/register': route_register,
        '/messages': route_message,
        '/messages/add': route_message_add,
    }
    return d
