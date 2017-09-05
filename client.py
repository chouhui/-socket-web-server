import socket
import ssl


def parsed_url(url):
    """
    解析 url 返回 (protocol host port path)
    """
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])
    else:
        # 检查端口
        port_dict = {
            'http': 80,
            'https': 443,
        }
        # 默认端口
        port = port_dict[protocol]

    return protocol, host, port, path


def response_by_socket(s):
    """
    参数是一个 socket 实例
    返回这个 socket 读取的所有数据
    """
    response = b''
    buffer_size = 1024
    # Connection: close 情况下循环收数据
    while True:
        r = s.recv(buffer_size)
        print("receive {} {}".format(len(r), r))
        if len(r) != 0:
            response += r
        else:
            return response


def socket_by_protocol(protocol):
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        s = ssl.wrap_socket(socket.socket())
    return s


def parsed_response(r):
    """
    解析出 状态码 header body
    """
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v

    return status_code, headers, body


def get(url):
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)

    s = socket_by_protocol(protocol)
    s.connect((host, port))
    request = 'GET {} HTTP/1.1\r\nhost: {}\r\nCookie: user=shlsshjkahkdahhs\r\nConnection: close\r\n\r\n'.format(
        path, host
    )
    s.send(request.encode())

    response = response_by_socket(s)
    r = response.decode()
    status_code, headers, body = parsed_response(r)

    if status_code == 301:
        url = headers['Location']
        return get(url)
    else:
        return response


def main():
    url = 'localhost:3000/login'
    response = get(url)
    print(response.decode())


if __name__ == '__main__':
    main()
