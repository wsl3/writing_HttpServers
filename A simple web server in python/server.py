"""
基本思想:

1.等待用户连接我们的站点并发送一个 HTTP 请求；
2.解析请求；
3.计算出它所请求的；
4.获取数据（或动态生成）；
5.格式化数据为 HTML；
5.返回数据。

步骤 1, 2, 6 都是从一个应用程序到另一个，Python 标准库有一个 'BaseHTTPServer' 模块，为我们实现这部分。
我们只需要关心步骤 3 - 5，这也是我们在下面的小程序中所做的。
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os

hosts = ("", 8080)


# Page = """<h2>Hello, WebServer!</h2>"""


class RequestHandler(BaseHTTPRequestHandler):
    def createPage(self):
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path
        }
        Page = '''\
    
        <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
        <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
        <tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
        <tr>  <td>Command</td>        <td>{command}</td>      </tr>
        <tr>  <td>Path</td>           <td>{path}</td>         </tr>
        
        '''
        self.Page = Page.format(**values)

    def sendPage(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(self.Page))
        self.end_headers()
        self.wfile.write(self.Page.encode())  # content body must be encoded to the type of byte

    def do_GET(self):
        try:
            fullPath = os.getcwd() + self.path

            # 查看请求的文件是否存在
            if not os.path.exists(fullPath):
                raise Exception(f"{self.path} don't exists!")
            # 查看请求的文件是否是单个文件
            elif os.path.isfile(fullPath):
                self.handle_file(fullPath)
            else:
                raise Exception("{} is Woring!".format(self.path))
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, fullPath):
        # 读取文件内容并发送
        try:
            with open(fullPath, "r") as read:
                content = read.read()
            self.send_content(content)
        except IOError as msg:
            msg = f"{self.path} can't be read: {msg}"
            self.handle_error(msg)

    def handle_error(self, msg):
        # 发送 error page
        content = f"""<h2>Error access: {self.path}</h2><p>{msg}</p>"""
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        # 发送数据
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(content))
        self.end_headers()

        self.wfile.write(content.encode())


if __name__ == "__main__":
    print("A simple web server is running!")
    server = HTTPServer(hosts, RequestHandler)
    server.serve_forever()
