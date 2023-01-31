# gui 채팅 클라이언트

import sys
import pymysql
import json
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
        self.stackedWidget.setCurrentIndex(0)
        self.initialize_socket(ip, port)
        self.listen_thread()
        self.btn_send.clicked.connect(self.send_chat)
        self.btn_enter.clicked.connect(self.chat_in)
        self.btn_exit.clicked.connect(self.chat_out)
        self.btn_back.clicked.connect(self.move_chatlist)
        self.lineEdit.returnPressed.connect(self.chat_in)
        self.sendmessage.returnPressed.connect(self.send_chat)
        self.chatroom.itemDoubleClicked.connect(self.move_chat)


    def chat_in(self):
        self.senders_name = self.lineEdit.text()
        if self.senders_name == '':
            QMessageBox.information(self, '알림', '사용자 이름을 입력해주세요')
            return
        self.stackedWidget.setCurrentIndex(1)
        self.client_socket.send('002'.encode('utf-8'))


    def chat_out(self):
        self.stackedWidget.setCurrentIndex(0)
        self.lineEdit.clear()
        self.receivemessage.clear()

    def move_chatlist(self):
        self.stackedWidget.setCurrentIndex(1)

    def move_chat(self):
        self.stackedWidget.setCurrentIndex(2)


    def initialize_socket(self, ip, port):
        ''' tcp socket을 생성하고 server와 연결 '''
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))


    # def chat_data(self):
    #     conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         f"SELECT * FROM chat WHERE send='{self.senders_name}' and IP='{ip}'")
    #     self.chattext = cursor.fetchall()
    #     print(self.chattext)
    #     conn.commit()
    #     conn.close()
    #     for i in range(len(self.chattext)):
    #         self.receivemessage.addItem(self.chattext[i][0] + ':' + self.chattext[i][1])



    def send_chat(self):
        ''' message를 전송하는 버튼 콜백 함수 '''
        data = self.sendmessage.text()
        # if data == '':
        #     QMessageBox.information(self, '알림', '메시지를 입력해주세요')
        #     return
        message = (self.senders_name + ':' + data + ':' + '001').encode('utf-8')
        self.receivemessage.addItem(self.senders_name + ':' + data)
        self.client_socket.send(message)
        self.sendmessage.clear()
        # self.receivemessage.scrollToBottom()
        return 'break'


    def listen_thread(self):
        ''' 데이터 수신 Thread를 생성하고 시작한다 '''
        t = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        t.start()


    def receive_message(self, so):
        while True:
            try:
                buf = so.recv(1024)  # 서버로부터 문자열 수신
                chat_msg = buf.decode('utf-8')
                print(chat_msg,"jhjjhhj")
                if not buf: # 문자열 없으면 연결이 종료됨
                    break
                if chat_msg[-3:] == '001':
                    self.receivemessage.addItem(chat_msg[:-4])
                elif chat_msg[-3:] == '002':
                    chatlog = json.loads(chat_msg[:-3])
                    for i in chatlog:
                        self.receivemessage.addItem(i[0] + ':' + i[1])
                        print(i,"hgtfr")
                    self.receivemessage.scrollToBottom()
            except:
                pass
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
