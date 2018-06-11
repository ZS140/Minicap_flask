import base64

from flask import Flask, render_template
import socket,sys
from flask_socketio import SocketIO, emit
import struct
import time

class Banner:
    def __init__(self):
        self.__banner = {
            'version': 0,  # 0：版本
            'length': 0,  # 1:该Banner信息的长度，方便循环使用
            'pid': 0,  # 2~5:相加得到进程id号
            'realWidth': 0,  # 6~9:累加得到设备真实宽度
            'realHeight': 0,  # 10~13:累加得到设备真实高度
            'virtualWidth': 0,  # 14~17:累加得到设备的虚拟宽度
            'virtualHeight': 0,  # 18~21:累加得到设备的虚拟高度
            'orientation': 0,  # 22:设备的方向
            'quirks': 0  # 23:设备信息获取策略
        }

    def __setitem__(self, key, value):
        self.__banner[key] = value

    def __getitem__(self, key):
        return self.__banner[key]

    def keys(self):
        return self.__banner.keys()

    def __str__(self):
        return str(self.__banner)


class Minicap(object):
    BUFFER_SIZE = 4096

    def __init__(self, host, port, banner):
        self.host = host
        self.port = port
        self.banner = banner

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(e)
            sys.exit(1)
        self.socket.connect((self.host, self.port))

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html',base64=base64)
@socketio.on('connect')
def f():
     print("f执行了")
@socketio.on('my event')
def handle(res):
    print(str(res))
    mc = Minicap('localhost', 1717, Banner())
    mc.connect()
    readBannerBytes = 0
    bannerLength = 24
    readFrameBytes = 0
    frameBodyLength = 0
    data = []
    while 1:
        try:
            chunk = mc.socket.recv(mc.BUFFER_SIZE)
        except socket.error as e:
            print("Error receiving data: %s" % e)
            sys.exit(1)
        cursor = 0  # 用于定位的游标
        buf_len = len(chunk)
        while cursor < buf_len:
            if readBannerBytes < bannerLength:  # 第一部分：前24个16进制为banner信息
                # print("执行了第一部分")
                list(map(lambda key, val: mc.banner.__setitem__(key, val), [key for key in mc.banner.keys()],
                         struct.unpack("<2b5ibB", chunk)))
                cursor = bannerLength
                readBannerBytes = bannerLength
                # print(self.banner)
            elif readFrameBytes < 4:  # 第二部分：4个字符的图片大小信息
                # print("执行了第二部分")
                frameBodyLength += (struct.unpack('B', chunk[cursor:cursor + 1])[0] << (readFrameBytes * 8))  # 累加获取图片大小
                cursor += 1
                readFrameBytes += 1
            else:
                # print("执行了第三部分")
                # print("frame length:%d buf_len:%d cursor:%d" % (frameBodyLength, buf_len, cursor))
                if buf_len - cursor >= frameBodyLength:
                    data.append(chunk[cursor:(cursor + frameBodyLength)])
                    emit('server_response', {'data': data})
                    cursor += frameBodyLength
                    frameBodyLength = readFrameBytes = 0
                    data = []
                else:
                    data.append(chunk[cursor:buf_len])
                    frameBodyLength -= buf_len - cursor
                    readFrameBytes += buf_len - cursor
                    cursor = buf_len



if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8090, debug=True)

# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# import random
#
# async_mode = None
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @socketio.on('my event')
# def handle_my_custom_event(json):
#     print('123')
#     print('received json: ' + str(json))
#     while True:
#         socketio.sleep(2)
#         t = random_int_list(1, 100, 10)
#         emit('server_response', {'data':t})
# def random_int_list(start, stop, length):
#     start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
#     length = int(abs(length)) if length else 0
#     random_list = []
#     for i in range(length):
#         random_list.append(random.randint(start, stop))
#     return random_list
#
#
# if __name__ == '__main__':
#     socketio.run(app, debug=True)