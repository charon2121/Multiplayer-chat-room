import wx
from socket import *
import threading


# 客户端继承wx.Frame, 就拥有了窗口界面
class Client(wx.Frame):
    # 参数是客户端的名字
    def __init__(self, c_name):  # 客户端名字
        # 调用父类的初始化函数
        wx.Frame.__init__(self, None, id=101, title='%s的客户端界面' % c_name, size=(400, 470))
        self.SetMaxSize((400, 470))
        self.SetMinSize((400, 470))
        # 添加窗口图标
        self.icon = wx.Icon('res/icon.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.icon)
        # 在窗口中初始化一个面板
        self.pl = wx.Panel(self)
        # 在面板里面放一些按钮，文本框，文本输入框等，将这些对象统一放入一个盒子中
        self.box = wx.BoxSizer(wx.VERTICAL)  # 在盒子中垂直方向进行自动排版

        self.g1 = wx.FlexGridSizer(wx.HORIZONTAL)  # 可伸缩的网格布局，水平方向进行布局
        # 创建两个按钮
        # 连接服务器按钮
        self.conn_button = wx.Button(self.pl, size=(200, 40), label="连接服务器")
        # 断开服务器按钮
        self.dis_conn_button = wx.Button(self.pl, size=(200, 40), label="断开服务器")
        # 将连接的按钮和断开的按钮放到网格中
        self.g1.Add(self.conn_button, 1, wx.TOP | wx.LEFT)  # 连接按钮布局在左边
        self.g1.Add(self.dis_conn_button, 1, wx.TOP | wx.RIGHT)  # 断开按钮布局在右边
        self.box.Add(self.g1, 1, wx.ALIGN_CENTRE)  # 两个按钮联合居中

        # 创建一个聊天内容的文本框，不能写消息 wx.TE_MULTILINE表示多行, wx.TE_READONLY表示只读
        self.text = wx.TextCtrl(self.pl, size=(400, 250), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.box.Add(self.text, 1, wx.ALIGN_CENTRE)

        # 创建一个聊天的输入文本框
        self.input_text = wx.TextCtrl(self.pl, size=(400, 100), style=wx.TE_MULTILINE)
        self.box.Add(self.input_text, 1, wx.ALIGN_CENTRE)

        # 创建发送和删除按钮
        self.g2 = wx.FlexGridSizer(wx.HORIZONTAL)  # 可伸缩的网格布局，水平方向进行布局
        self.clear_button = wx.Button(self.pl, size=(200, 40), label="删除")
        self.send_button = wx.Button(self.pl, size=(200, 40), label="发送")
        self.g2.Add(self.clear_button, 1, wx.TOP | wx.LEFT)
        self.g2.Add(self.send_button, 1, wx.TOP | wx.RIGHT)
        self.box.Add(self.g2, 1, wx.ALIGN_CENTRE)

        self.pl.SetSizer(self.box)  # 将盒子放进面板中

        '''以上代码完成了客户端的窗口设计'''

        '''给所有按钮绑定点击事件'''
        # 连接按钮
        self.Bind(wx.EVT_BUTTON, self.connect_to_server, self.conn_button)
        # 发送按钮
        self.Bind(wx.EVT_BUTTON, self.send_to, self.send_button)
        # 断开按钮
        self.Bind(wx.EVT_BUTTON, self.go_out, self.dis_conn_button)
        # 清除按钮
        self.Bind(wx.EVT_BUTTON, self.reset, self.clear_button)

        '''客户端的属性'''
        self.name = c_name
        self.isConnected = False  # 客户端是否已经连上了服务器
        self.client_socket = None

    def connect_to_server(self, event):
        print(f'客户端{self.name}开始连接服务器')
        if not self.isConnected:
            self.isConnected = True
            server_host_port = ('localhost', 8888)
            # 发送一个连接的请求
            # 创建一个socket
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(server_host_port)
            # 之前规定的客户端只要连接成功，马上把自己的名字发给服务器
            self.client_socket.send(self.name.encode('UTF-8'))
            t = threading.Thread(target=self.receive_data)
            t.setDaemon(True)  # 客户端关闭，当前守护线程也自动关闭
            t.start()

    # 接收服务器发送过来的请求
    # 服务器在接收到客户端连接之后，需要在文本框中显示一个提示信息
    # 并且需要通知所有的客户端
    def receive_data(self):
        print('客户端准备接收服务器的数据')
        while self.isConnected:
            data = self.client_socket.recv(1024).decode('UTF-8')
            # 从服务器接收到数据需要显示，找到文本框
            self.text.AppendText(f'{data}\n')

    # 发送消息功能实现
    def send_to(self, event):
        if self.isConnected:
            info = self.input_text.GetValue()
            if info != '':
                self.client_socket.send(info.encode('UTF-8'))
                # 发送之后输入框重置为空
                self.input_text.SetValue('')

    # 客户端离开聊天室功能实现
    def go_out(self, event):
        self.client_socket.send('A^disconnect^B'.encode('UTF-8'))
        # 客户端主线程关闭
        self.isConnected = False

    # 客户端输入框信息的重置
    def reset(self, event):
        self.input_text.Clear()


if __name__ == '__main__':
    app = wx.App()
    name = input("客户端的名字：")
    Client(name).Show()
    # 循环刷新显示窗口
    app.MainLoop()
