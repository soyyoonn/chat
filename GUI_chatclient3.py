# GUI 채팅 클라이언트
import json
from socket import *
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import threading
from datetime import datetime

form_class = uic.loadUiType("sy_chatclient.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('채팅프로그램')

        self.initialize_socket()                         # 소켓생성 및 서버와 연결
        self.btn_enter.clicked.connect(self.nick_check)   # 닉네임 체크
        self.btn_exit.clicked.connect(self.main_page)    # 채팅방 나가기 눌렀을시 메인으로 이동
        self.chatroom.itemClicked.connect(self.itme_widget)
        self.chatroom.itemDoubleClicked.connect(self.chat_page) # 채팅방 더블클릭했을 때
        self.btn_back.clicked.connect(self.list_page)       # 채팅방 리스트 페이지 이동
        self.btn_send.clicked.connect(self.send_chat)    # 전송버튼 누를시 서버에 메시지 전송
        self.btn_makechat.clicked.connect(self.newroom_chat)     # 채팅방 생성눌렀을때
        # self.send_line.returnPressed.connect(self.send_chat)

        self.start()

        self.stackedWidget.setCurrentIndex(0)

    # 소켓생성 및 서버와 연결
    def initialize_socket(self):
        ip = '10.10.21.124'
        port = 9066
        self.client_socket=socket(AF_INET,SOCK_STREAM)
        self.client_socket.connect((ip,port))

    # 시작시 닉네임 리스트 가져오기
    def start(self):
        self.client_socket.send(('010').encode()) # 010 : 닉네임증복확인용 닉네임리스트 받기

    # 채팅방 이름, 행번호 가져오기
    def itme_widget(self):
        self.row = self.chatroom.currentRow()
        self.item = self.chatroom.currentItem()

    # 닉네임 중복체크
    def nick_check(self):
        if len(self.j_data10) == 0:
            self.client_socket.send((f'{self.username.text()}' + '003').encode())  # 008 : 닉네임 저장
            self.stackedWidget.setCurrentIndex(1)
            self.client_socket.send('009'.encode())  # 009 : 채팅방 리스트
        else:
            if self.j_data10[:3][0] == self.username.text():
                QMessageBox.information(self,'알림','닉네임 중복')
            else :
                self.client_socket.send((f'{self.username.text()}'+'003').encode()) # 008 : 닉네임 저장
                self.client_socket.send('009'.encode()) # 009 : 채팅방 리스트
                self.stackedWidget.setCurrentIndex(1)

    def list_page(self):
        self.chatroom.clear()
        self.client_socket.send('009'.encode())  # 009 : 채팅방 리스트
        self.stackedWidget.setCurrentIndex(1)

    def chat_page(self):
        self.receivemessage.clear()
        self.stackedWidget.setCurrentIndex(2)
        self.client_socket.send(('005').encode())  # 005 : 현재접속자 명단
        self.chat_title.setText(f'{self.item.text()}')
        self.client_socket.send((f'{self.item.text()}004+001+{self.username.text()}011').encode())
        self.receivemessage.scrollToBottom()

    # # 종료시 현재접속자에서 삭제
    # def closeEvent(self, event):
    #     quit_msg = "종료하시겠습니까?"
    #     reply = QMessageBox.question(self, '종료', quit_msg, QMessageBox.Yes, QMessageBox.No)
    #
    #     if reply == QMessageBox.Yes:
    #         self.client_socket.send((self.name_line.text() + '007').encode())  # 007 : 현재접속자 삭제
    #         event.accept()
    #     else:
    #         event.ignore()
    #
    def newroom_chat(self):
        self.client_socket.send((self.newchatname.text()+'006').encode()) # 006 : 새로운 채팅방
        self.newchatname.clear()

    # 현재 선택한 리스트 위젯의 행과 명칭 알려줌
    def main_page(self):
        self.username.clear()                              # 닉네임 삭제
        self.stackedWidget.setCurrentIndex(0)
        # self.susin_list.clear()
        # self.listWidget_2.clear()
        # self.client_socket.send((self.name_line.text() + '007').encode())  # 007 : 현재접속자 삭제

    # message를 전송하는 콜백함수
    # 송신메시지 창에서 메시지를 읽어 전송
    def send_chat(self):
        senders_name=self.username.text()                    # 사용자 이름 받아오기
        data=self.sendmessage.text()                         # 송신메시지 받아오기
        roomname=self.item.text()
        message=(f'{roomname}004+{senders_name}:{data}002+0')     # 서버로 사용자이름, 송신메시지, 채팅방이름 전송준비
        self.client_socket.send(message.encode())            # 서버전송 : 메시지
        self.sendmessage.clear()                             # 작성한 송신메시지 삭제


    # 소켓에서 메시지를 읽어서 수신메시지 창에 표시
    def receive_message(self,so):
        while True:
            try:
                buf = so.recv(2048)
                if not buf:
                    # so.close()
                    break
            except Exception as e:
                print(e)
                # break
            else:  #
                recv_data = buf.decode()  # 메시지 문자열로 변환
                print(recv_data)
                if recv_data[-3:] == '010':                 # 현재 접속 닉네임
                    self.j_data10 = json.loads(recv_data[:-3])

                if recv_data[-3:] == '009':                 # 채팅방목록 보여주기
                    self.chatroom.clear()
                    j_data4 = json.loads(recv_data[:-3])
                    for i in j_data4:
                        self.chatroom.addItem(f'{i[0]}')

                if recv_data[-3:] == '005':               # 현재 접속자 명단
                    self.chatmember.clear()
                    j_data5 = json.loads(recv_data[:-3])
                    print(j_data5)
                    for i in range(len(j_data5)):
                        self.chatmember.addItem(j_data5[i])

                if recv_data[-3:] == '001':                 # 지난 채팅내역 띄우기
                    j_data1 = json.loads(recv_data[:-3])
                    for i in j_data1:
                        self.receivemessage.addItem(f'[{i[0]}:{i[1]}]\n{i[2]}')
                    self.receivemessage.addItem(f'------------- 이전채팅내역 -------------')

                if recv_data[-3:] == '004':
                    j_data4 = json.loads(recv_data[:-3])
                    self.roomname_check = j_data4

                if recv_data[-3:] == '011':                 # 채팅방 입장알리기
                    j_data11 = json.loads(recv_data[:-3])
                    if self.roomname_check == self.item.text():
                        self.receivemessage.addItem(f'---------- {j_data11}님 채팅방 입장 ----------')
                    else:
                        pass

                if recv_data[-3:] == '002':          # 실시간 채팅 내역 띄우기
                    j_data2 = json.loads(recv_data[:-3])
                    if self.roomname_check == self.item.text():
                        for i in j_data2:
                            self.receivemessage.addItem(f'[{i[0]}:{i[1]}]\n{i[2]}')
                    else:
                        pass






if __name__=='__main__':
    app = QApplication(sys.argv)     #QApplication : 프로그램을 실행시켜주는 클래스
    myWindow = WindowClass()         #WindowClass의 인스턴스 생성
    myWindow.show()                  #프로그램 화면을 보여주는 코드
    cThread = threading.Thread(target=myWindow.receive_message, args=(myWindow.client_socket,))
    cThread.daemon = True  # 메인스레드가 끝날때 같이 종료됨, 아니면 계속 스레드 돌아감
    cThread.start()
    app.exec_()                      #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드