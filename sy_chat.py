# gui 채팅 클라이언트

import sys
import pymysql
from socket import *
from threading import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
form_class = uic.loadUiType('./chatclient.ui')[0]

class Main(QMainWindow, form_class):
    client_socket = None

    def __init__(self, ip, port):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket(ip, port)
        self.listen_thread()
        self.btn_send.clicked.connect(self.send_chat)
        self.sendmessage.returnPressed.connect(self.send_chat)

    def initialize_socket(self, ip, port):
        ''' tcp socket을 생성하고 server와 연결 '''
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))

    def send_chat(self):
        ''' message를 전송하는 버튼 콜백 함수 '''
        senders_name = self.lineEdit.text()
        # if senders_name == '':
        #     QMessageBox.information(self, '알림', '사용자 이름을 입력해주세요')
        #     return
        data = self.sendmessage.text()
        # if data == '':
        #     QMessageBox.information(self, '알림', '메시지를 입력해주세요')
        #     return
        message = (senders_name + ' : ' + data).encode('utf-8')
        self.receivemessage.addItem(message.decode('utf-8'))
        self.client_socket.send(message)
        self.sendmessage.clear()
        return 'break'

    def listen_thread(self):
        ''' 데이터 수신 Thread를 생성하고 시작한다 '''
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()

    def receive_message(self, so):
        while True:
            buf = so.recv(256)
            if not buf: # 연결이 종료됨
                break
            self.receivemessage.addItem(buf.decode('utf-8'))
        so.close()

if __name__ == "__main__":
    ip = input("server IP addr: ")
    if ip == '':
        ip = '10.10.21.101'
    port = 9180
    app = QApplication(sys.argv)
    mainWindow = Main(ip, port)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(720)
    widget.setFixedWidth(650)
    widget.show()
    app.exec_()
