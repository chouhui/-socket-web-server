import socket
import urllib.parse

from utils import log
import _thread

from routes import route_static
from routes import route_dict


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.raw_data = ''

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


def error(code=404):
    """
    根据 code 返回不同的错误响应，此处只写了404的响应
    """
    e = {
        404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def parsed_path(path):
    """
    输入: /name?message=hello&author=world
    返回
    (name, {
        'message': 'hello',
        'author': 'world',
    })
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(request):
    path, query = parsed_path(request.path)
    request.path = path
    request.query = query
    """
    根据path来调用对应的函数
    """
    r = {
        '/static': route_static,
    }
    r.update(route_dict())
    response = r.get(path, error)
    return response(request)


def process_request(connection):
    r = connection.recv(1024)
    r = r.decode()
    request = Request()
    request.raw_data = r
    # 设置Request的参数
    header, request.body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    parts = h[0].split()
    request.path = parts[1]
    request.method = parts[0]
    # 用 response_for_path 函数来得到 path 对应的响应内容
    response = response_for_path(request)
    # 把响应发送给客户端
    connection.sendall(response)

    # 处理完请求, 关闭连接
    connection.close()


def run(host='', port=3000):
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        while True:
            # 监听 接受 读取请求数据 解码成字符串
            s.listen(5)
            connection, address = s.accept()
            log('ip {}'.format(address))
            _thread.start_new_thread(process_request, (connection, ))




if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='127.0.0.1',
        port=3000,
    )
    run(**config)
