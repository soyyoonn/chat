# GUI 채팅 클라이언트
from socket import *
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import threading

form_class = uic.loadUiType("chat.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.initialize_socket()                         # 소켓생성 및 서버와 연결
        self.send_btn.clicked.connect(self.send_chat)    # 전송버튼 누를시 서버에 메시지 전송

    # 소켓생성 및 서버와 연결
    def initialize_socket(self):
        ip = input('server IP addr: ')
        if ip == '':
            ip = '192.168.125.10'
        port = 2500
        self.client_socket=socket(AF_INET,SOCK_STREAM)
        self.client_socket.connect((ip,port))

    # message를 전송하는 콜백함수
    # 송신메시지 창에서 메시지를 읽어 수신메시지 창에 표시하고 전송
    def send_chat(self):
        senders_name=self.name_line.text()                   # 사용자 이름 받아오기
        data=self.send_line.toPlainText()                    # 송신메시지 받아오기
        self.recv_bra.append(f'{senders_name} : {data}')     # 수신메시지 텍스트 브라우저에 띄우기
        message=(f'{senders_name} : {data}').encode('utf-8') # 서버로 사용자이름, 송신메시지 보낼 준비
        self.client_socket.send(message)                     # 서버로 전송
        self.send_line.clear()                               # 작성한 송신메시지 삭제

    # 소켓에서 메시지를 읽어서 수신메시지 창에 표시
    def receive_message(self,so):
        while True:
            buf=so.recv(256)                                # 서버로부터 받은 메시지가 있으면
            if not buf: # 연결 종료
                break
            recv_data=buf.decode()                          # 메시지 문자열로 변환
            print(recv_data)
            self.recv_bra.append(f'{recv_data}')            # 수신메시지 텍스트 브라우저에 띄우기
        so.close()

if __name__=='__main__':
    app = QApplication(sys.argv)     #QApplication : 프로그램을 실행시켜주는 클래스
    myWindow = WindowClass()         #WindowClass의 인스턴스 생성
    myWindow.show()                  #프로그램 화면을 보여주는 코드
    cThread=threading.Thread(target=myWindow.receive_message, args=(myWindow.client_socket,))
    cThread.daemon=True              # 메인스레드가 끝날때 같이 종료됨, 아니면 계속 스레드 돌아감
    cThread.start()
    app.exec_()                      #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드

