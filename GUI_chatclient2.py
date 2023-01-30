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
        self.setWindowTitle('채팅프로그램')

        self.initialize_socket()                         # 소켓생성 및 서버와 연결
        self.send_btn.clicked.connect(self.send_chat)    # 전송버튼 누를시 서버에 메시지 전송
        self.go_btn.clicked.connect(self.chat_page)      # 채팅방 입장 눌렀을 시 채팅으로 이동
        self.exit_btn.clicked.connect(self.main_page)    # 채팅방 나가기 눌렀을시 닉네임입력칸으로 이동

        cThread = threading.Thread(target=self.receive_message, args=(self.client_socket,))
        cThread.daemon = True  # 메인스레드가 끝날때 같이 종료됨, 아니면 계속 스레드 돌아감
        cThread.start()

        self.stackedWidget.setCurrentIndex(0)

    def chat_page(self):
        self.stackedWidget.setCurrentIndex(1)
        alarm = (f'알림:"{self.name_line.text()}" 님이 채팅방에 입장하셨습니다').encode('utf-8')
        self.client_socket.send(alarm)                      # 서버로 전송

    def main_page(self,sock):
        self.name_line.clear()                              # 닉네임 삭제
        self.recv_bra.clear()                               # 텍스트 브라우저 내용 삭제
        self.stackedWidget.setCurrentIndex(0)

    # 소켓생성 및 서버와 연결
    def initialize_socket(self):
        ip = '10.10.21.124'
        port = 9523
        self.client_socket=socket(AF_INET,SOCK_STREAM)
        self.client_socket.connect((ip,port))
        print(self.client_socket)

    # message를 전송하는 콜백함수
    # 송신메시지 창에서 메시지를 읽어 전송
    def send_chat(self):
        senders_name=self.name_line.text()                   # 사용자 이름 받아오기
        data=self.send_line.toPlainText()                    # 송신메시지 받아오기
        # a=self.recv_bra.append(f'{senders_name} : {data}')   # 수신메시지 텍스트 브라우저에 띄우기
        message=(f'{senders_name}:{data}').encode('utf-8') # 서버로 사용자이름, 송신메시지 보낼 준비
        self.client_socket.send(message)                     # 서버로 전송
        self.send_line.clear()                               # 작성한 송신메시지 삭제

    # 소켓에서 메시지를 읽어서 수신메시지 창에 표시
    def receive_message(self,so):
        print(so)
        while True:
            buf=so.recv(256)                                # 서버로부터 받은 메시지가 있으면
            print(buf)
            recv_data=buf.decode()                          # 메시지 문자열로 변환
            print(recv_data)
            a=self.recv_bra.append(f'{recv_data}')            # 수신메시지 텍스트 브라우저에 띄우기
            self.recv_bra.scrollToAnchor(a)                   # 앵커 위치로 스크롤 함.
            if not buf: # 연결 종료
                print('연결이 종료되었습니다')
                pass

if __name__=='__main__':
    app = QApplication(sys.argv)     #QApplication : 프로그램을 실행시켜주는 클래스
    myWindow = WindowClass()         #WindowClass의 인스턴스 생성
    myWindow.show()                  #프로그램 화면을 보여주는 코드
    app.exec_()                      #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드

