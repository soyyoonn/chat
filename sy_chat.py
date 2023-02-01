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
form_class = uic.loadUiType('./sy_chatclient.ui')[0]

class Main(QMainWindow, form_class):
    client_socket = None
    def __init__(self, ip, port):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)
        self.initialize_socket(ip, port)
        self.listen_thread()
        self.btn_send.clicked.connect(self.send_chat)   # 전송 버튼 누르면 채팅 보내기
        self.btn_enter.clicked.connect(self.chat_in)    # 확인 버튼 누르면 채팅 목록으로 이동
        self.btn_exit.clicked.connect(self.chat_out)    # 나가기 버튼 누르면 첫 화면으로 이동
        self.btn_back.clicked.connect(self.move_chatlist)   # 뒤로가기 버튼 누르면 채팅 목록으로 이동
        self.username.returnPressed.connect(self.chat_in)   # 사용자 이름 엔터키로 전송
        self.sendmessage.returnPressed.connect(self.send_chat)   # 채팅 엔터키로 전송
        self.chatroom.itemDoubleClicked.connect(self.move_chat)  # 채팅 목록에서 더블클릭하면 채팅방으로 이동
        self.newchatname.returnPressed.connect(self.make_newchat)    # 채팅방 이름 엔터키로 전송
        self.btn_makechat.clicked.connect(self.make_newchat)   # 채팅방 만들기 버튼 누르면 채팅방 생성


    def chat_in(self): # 채팅 목록으로 이동
        self.senders_name = self.username.text()
        if self.senders_name == '':  # 사용자 이름이 입력 안됐을 경우
            QMessageBox.information(self, '알림', '사용자 이름을 입력해주세요')
            return
        self.stackedWidget.setCurrentIndex(1)
        self.client_socket.send('002'.encode('utf-8'))

    def chat_out(self):  # 채팅방 나가기
        self.stackedWidget.setCurrentIndex(0)
        self.username.clear()  # 사용자 이름 클리어
        self.chatroom.clear()  # 채팅목록 클리어

    def move_chatlist(self):  # 채팅목록으로 이동
        self.stackedWidget.setCurrentIndex(1)
        # self.receivemessage.clear()  # 채팅방 클리어

    def move_chat(self):  # 채팅방으로 이동
        self.stackedWidget.setCurrentIndex(2)
        self.a = self.chatroom.currentItem().text()
        msg = (self.a + ':003').encode('utf-8')
        self.client_socket.send(msg)


    def initialize_socket(self, ip, port):
        ''' tcp socket을 생성하고 server와 연결 '''
        self.client_socket = socket(AF_INET, SOCK_STREAM)  # 클라이언트 소켓 생성
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))  # 서버와 소켓 연결

    def send_chat(self):
        ''' message를 전송하는 버튼 콜백 함수 '''
        data = self.sendmessage.text()
        # if data == '':
        #     QMessageBox.information(self, '알림', '메시지를 입력해주세요')
        #     return
        message = (self.senders_name + ':' + data + ':' + self.a + ':' + '001').encode('utf-8')  # 서버로 보낼 메시지
        self.receivemessage.addItem(self.senders_name + ':' + data)  # 채팅창(리스트 위젯)에 메시지 추가
        self.client_socket.send(message)  # 메시지 서버로 전송
        self.sendmessage.clear()  # 메시지 보내는 창 클리어
        return 'break'

    def make_newchat(self):
        chatname = self.newchatname.text()
        if chatname == '':
            return
        print('ddddd')
        self.client_socket.send((chatname + ':' +'004').encode('utf-8'))
        print('ㅗㅗㅗㅗㅗ')
        self.newchatname.clear()

    def listen_thread(self):
        ''' 데이터 수신 Thread를 생성하고 시작한다 '''
        t = Thread(target=self.receive_message, args=(self.client_socket,), daemon=True)
        t.start()


    def receive_message(self, so):  # 서버에서 메시지를 받는다
        while True:
            try:
                buf = so.recv(1024)  # 서버로부터 문자열 수신
                chat_msg = buf.decode('utf-8')
                print(chat_msg,"jhjjhhj")
                if not buf:  # 문자열 없으면 연결이 종료됨
                    break
                if chat_msg[-3:] == '001':  # 받은 메시지 마지막 3글자가 001일때
                    self.receivemessage.addItem(chat_msg[:-4])  # 채팅창에 메시지 추가

                elif chat_msg[-3:] == '002':   # 받은 메시지 마지막 3글자가 002 일때
                    chatroom = json.loads(chat_msg[:-3])
                    for i in chatroom:
                        self.chatroom.addItem(i[0])  # 채팅방 목록 불러오기
                        print(i[0])

                elif chat_msg[-3:] == '003':  # 받은 메시지 마지막 3글자가 003 일때
                    self.receivemessage.clear()
                    chatlog = json.loads(chat_msg[:-3])  # json으로 변환한 리스트 로드
                    for i in chatlog:
                        self.receivemessage.addItem(i[0] + ':' + i[1])  # 채팅창에 메시지 추가
                        print(i)
                    self.receivemessage.scrollToBottom()

                elif chat_msg[-3:] == '004':
                    self.chatroom.addItem(chat_msg[:-3])

            except:
                pass
        so.close()


if __name__ == "__main__":
    ip = '10.10.21.101'
    port = 9180
    app = QApplication(sys.argv)
    mainWindow = Main(ip, port)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(780)
    widget.setFixedWidth(650)
    widget.show()
    app.exec_()
