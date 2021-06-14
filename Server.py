import wx
from socket import *
import threading
import time


class Server(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=102, title='服务器界面', size=(400, 470))
        # 固定窗口的大小
        self.SetMaxSize((400, 470))
        self.SetMinSize((400, 470))
        # 添加窗口图标
        self.icon = wx.Icon('res/server.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.icon)

        pl = wx.Panel(self)  # 在窗口中初始化一个面板
        # 在面板里面放一些按钮，文本框，文本输入框等，将这些对象统一放入一个盒子中
        self.box = wx.BoxSizer(wx.VERTICAL)  # 在盒子中垂直方向进行自动排版
        self.g1 = wx.FlexGridSizer(wx.HORIZONTAL)  # 可伸缩的网格布局，水平方向进行布局
        # 创建三个按钮，启动服务器按钮，保存聊天记录按钮，停止服务按钮
        self.start_button = wx.Button(pl, size=(133, 40), label="启动")
        self.save_button = wx.Button(pl, size=(133, 40), label="保存")
        self.stop_button = wx.Button(pl, size=(133, 40), label="停止")
        # 将连接的按钮和断开的按钮放到网格中
        self.g1.Add(self.start_button, 1, wx.TOP)  # 开始按钮布局在左边
        self.g1.Add(self.save_button, 1, wx.TOP)  # 结束按钮布局在右边
        self.g1.Add(self.stop_button, 1, wx.TOP)  # 保存按钮布局在中间
        self.box.Add(self.g1, 1, wx.ALIGN_CENTRE)  # 三个按钮联合居中
        # 创建一个只读的文本框用于显示聊天记录
        self.text = wx.TextCtrl(pl, size=(400, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.box.Add(self.text, 1, wx.ALIGN_CENTRE)
        # 将box和面板绑定在一起
        pl.SetSizer(self.box)
        '''以上代码创建窗口结束'''

        '''服务器准备执行的一些属性'''
        self.isOn = False
        self.host_port = ('', 8888)
        # 创建一个使用tcp协议的套接字
        # AF_INET -> 使用的是ipv4的地址
        # SOCK_STREAM -> 使用tcp的连接
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(self.host_port)
        # 进行监听客户端的等待
        self.server_socket.listen(5)
        # 进行对客户端线程和session线程进行管理
        self.session_thread_map = {}
        # 服务器的启动
        '''给所有的按钮绑定一个事件'''
        # 给启动按钮绑定一个按钮事件，事件触发的函数会自动调用
        # 开启按钮
        self.Bind(wx.EVT_BUTTON, self.start_server, self.start_button)
        # 保存按钮
        self.Bind(wx.EVT_BUTTON, self.save_record, self.save_button)
        # 停止按钮
        self.Bind(wx.EVT_BUTTON, self.stop_server, self.stop_button)

    # 启动按钮
    # @staticmethod
    # do_work是主线程
    def start_server(self, event):
        if self.isOn:
            print('服务器已经启动')
            return
        self.isOn = True
        main_thread = threading.Thread(target=self.do_work)
        # 设置为守护线程
        main_thread.setDaemon(True)
        # 启动主线程
        print('服务器开始启动')
        main_thread.start()

    # 主线程
    def do_work(self):
        print('服务器开始工作')
        while self.isOn:
            session_socket, client_addr = self.server_socket.accept()
            # 客户端发送请求的时候，客户端会发自己的名字过来
            # 服务器首先接收客户端发过来的第一条消息，规定第一条消息为客户端的名字
            usr_name = session_socket.recv(1024).decode(encoding='UTF-8')  # 接收客户端的名字
            # 创建一个会话的线程
            session_thread = SessionThread(session_socket, usr_name, self)
            self.session_thread_map[usr_name] = session_thread
            session_thread.start()
            # 表示有客户端进入了聊天室
            self.show_info_send_client("系统", f'欢迎{usr_name}进入聊天室!',
                                       time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.server_socket.close()

    # 在文本中显示聊天信息，同时发给所有的客户端
    # source 信息源
    # data 信息
    # data_time 发送这条信息的时间
    def show_info_send_client(self, source, data, data_time):
        send_data = f'{source} : {data}\n时间: {data_time}\n'  # 在服务器中显示
        self.text.AppendText('\n' + send_data)
        for client in self.session_thread_map.values():
            if client.isOn:  # 当前客户端是活动的
                client.usr_socket.send(send_data.encode('UTF-8'))

    # 服务器保存聊天记录的内容
    def save_record(self, event):
        record = self.text.GetValue()
        with open('recode.txt', 'w', encoding='utf-8') as f:
            f.write(record)

    # 服务器停止服务功能
    def stop_server(self, event):
        self.show_info_send_client("系统:", f'当前聊天室已经关闭！',
                                   time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.isOn = False
        self.server_socket.close()
        exit()


# 服务端会话线程的类
class SessionThread(threading.Thread):
    def __init__(self, usr_socket, usr_name, server):
        threading.Thread.__init__(self)
        self.usr_socket = usr_socket
        self.usr_name = usr_name
        self.server = server
        # 会话线程是否启动
        self.isOn = True

    def run(self):
        # 线程执行的功能，和客户端进行交互
        print(f'客户端{self.usr_name}已经和服务器连接成功，服务器启动一个会话线程')
        while self.isOn:
            # 接收客户端的聊天信息
            data = self.usr_socket.recv(1024).decode('UTF-8')
            # 如果客户端点击了断开按钮，首先发一条消息给服务器
            # A^disconnect^B 用来控制客户端的开启或者关闭
            if data == 'A^disconnect^B':
                self.isOn = False
                # 有用户离开了需要通知其他用户
                self.server.show_info_send_client("系统", f'{self.usr_name}离开聊天室!',
                                                  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            # 其他的聊天信息应该显示给所有的客户端
            else:
                self.server.show_info_send_client(self.usr_name, data,
                                                  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            # 保持和客户端的会话的socket关闭
        self.usr_socket.close()


if __name__ == '__main__':
    server = wx.App()
    Server().Show()
    server.MainLoop()
