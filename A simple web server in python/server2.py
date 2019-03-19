"""
    服务器接受到的请求种类, 及处理方式：
    1. 不存在, 返回error page
    2. 单一文件, 返回文件内容
    3. 目录, 如果目录下有 index.html，则返回index, 否则返回目录下的文件名
    4. finally, 返回error page
"""




from http.server import HTTPServer, BaseHTTPRequestHandler
import os

hosts = ("", 8080)


class file_not_exist(object):
    def test(self, handler):
        return not os.path.exists(handler.fullPath)

    def act(self, handler):
        raise Exception(f"{handler.path} not exists!")


class is_file(object):
    def test(self, handler):
        return os.path.isfile(handler.fullPath)

    def act(self, handler):
        handler.handle_file(handler.fullPath)


class is_dir(object):
    def have_index(self, handler):
        self.filePath = os.path.join(handler.fullPath, "index.html")
        return os.path.isfile(self.filePath)

    def list_dir(self, handler):
        file_list = os.listdir(handler.fullPath)
        file_list = [i for i in file_list if not i.startswith(".")]
        file_list_string = "<br>".join(file_list)
        handler.send_content(file_list_string)

    def test(self, handler):
        return os.path.isdir(handler.fullPath)

    def act(self, handler):
        if self.have_index(handler):
            handler.handle_file(self.filePath)
        else:
            self.list_dir(handler)



class finally_case(object):
    def test(self, handler):
        return True

    def act(self, handler):
        raise Exception(f"{handler.path} is woring!")


Cases = [
    file_not_exist(),
    is_file(),
    is_dir(),
    finally_case()
]


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            self.fullPath = os.getcwd() + self.path

            # check the method to deal with the request
            for case in Cases:
                if case.test(self):
                    case.act(self)
                    break
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
    print("A simple web server2 is running!")
    server = HTTPServer(hosts, RequestHandler)
    server.serve_forever()
