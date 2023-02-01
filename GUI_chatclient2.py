# GUI 채팅 클라이언트
import json
from socket import *
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import threading
import time

form_class = uic.loadUiType("chat.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('채팅프로그램')

        self.initialize_socket()                         # 소켓생성 및 서버와 연결
        self.send_btn.clicked.connect(self.send_chat)    # 전송버튼 누를시 서버에 메시지 전송
        self.go_btn.clicked.connect(self.chat_page)      # 채팅방 입장 눌렀을 시 채팅으로 이동
        self.exit_btn.clicked.connect(self.main_page)    # 채팅방 나가기 눌렀을시 닉네임입력칸으로 이동
        self.send_line.returnPressed.connect(self.send_chat)
        self.chat_list.itemClicked.connect(self.itme_widget)

        self.stackedWidget.setCurrentIndex(0)
    def itme_widget(self):
        self.row = self.chat_list.currentRow()
        self.item = self.chat_list.currentItem()

    def chat_page(self):
        print(self.row)
        self.stackedWidget.setCurrentIndex(1)
        if self.row == 0:
            self.chat_title.setText('채팅방1')
            self.label_5.setText(f'{self.name_line.text()}님 환영합니다')
            self.client_socket.send('001'.encode())                             # 001 : 이전내역
            self.client_socket.send((self.name_line.text() + '003').encode())   # 003 : 접속 닉네임
            time.sleep(0.5)
            self.client_socket.send((self.item.text() + '004').encode())        # 004 : 채팅방이름(DB저장)
            time.sleep(0.5)
            self.client_socket.send(('005').encode())                           # 005 : 현재접속자 명단
            self.susin_list.scrollToBottom()

        else:
            pass
    def main_page(self):
        self.name_line.clear()                              # 닉네임 삭제
        self.susin_list.clear()
        self.listWidget_2.clear()
        self.stackedWidget.setCurrentIndex(0)

    # 소켓생성 및 서버와 연결
    def initialize_socket(self):
        ip = '10.10.21.124'
        port = 9014
        self.client_socket=socket(AF_INET,SOCK_STREAM)
        self.client_socket.connect((ip,port))

    # message를 전송하는 콜백함수
    # 송신메시지 창에서 메시지를 읽어 전송
    def send_chat(self):
        senders_name=self.name_line.text()                   # 사용자 이름 받아오기
        data=self.send_line.text()                           # 송신메시지 받아오기
        message=(f'{senders_name}:{data}')                   # 서버로 사용자이름, 송신메시지 보낼 준비
        self.client_socket.send((message+'002').encode())    # 서버전송 : 메시지
        self.send_line.clear()                               # 작성한 송신메시지 삭제

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
                if recv_data[-3:] == '001':  # 지난 채팅내역 띄우기
                    j_data = json.loads(recv_data[:-3])
                    for i in j_data:
                        self.susin_list.addItem(f'{i[0]}:{i[1]}')
                    self.susin_list.addItem(f'------------- 이전채팅내역 -------------')
                elif recv_data[-3:] == '003':  # 입장알리기
                    j_data1 = json.loads(recv_data[:-3])
                    self.susin_list.addItem(f'---------- {j_data1}님 채팅방 입장 ----------')
                elif recv_data[-3:] == '002':  # 실시간 채팅 내역 띄우기
                    j_data2 = json.loads(recv_data[:-3])
                    self.susin_list.addItem(j_data2)
                elif recv_data[-3:] == '005':  # 현재 접속자 명단
                    self.listWidget_2.clear()
                    j_data3 = json.loads(recv_data[:-3])
                    print(j_data3)
                    for i in range(len(j_data3)):
                        self.listWidget_2.addItem(j_data3[i])


if __name__=='__main__':
    app = QApplication(sys.argv)     #QApplication : 프로그램을 실행시켜주는 클래스
    myWindow = WindowClass()         #WindowClass의 인스턴스 생성
    myWindow.show()                  #프로그램 화면을 보여주는 코드
    cThread = threading.Thread(target=myWindow.receive_message, args=(myWindow.client_socket,))
    cThread.daemon = True  # 메인스레드가 끝날때 같이 종료됨, 아니면 계속 스레드 돌아감
    cThread.start()
    app.exec_()                      #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드