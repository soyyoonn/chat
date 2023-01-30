# GUI 채팅 클라이언트

from socket import *
from tkinter import *   # GUI 환경에서 전송데이터와 수신데이터를 표시하도록 tkinter 모듈 사용
from tkinter.scrolledtext import ScrolledText
from threading import *

class ChatClient:
    client_socket=None

    def __init__(self,ip,port):
        self.initialize_socket(ip,port) # TCP소켓 생성, 서버연결
        self.initialize_gui()           # 위젯 배치, 사용자 화면 구성
        self.listen_thread()            # receive_message()를 실행하는 스레드를 생성하고 시작

    def initialize_socket(self,ip,port):
        self.client_socket=socket(AF_INET,SOCK_STREAM)
        remote_ip=ip
        remote_port=port
        self.client_socket.connect((remote_ip,remote_port))

    # 위젯배치, 초기화
    def initialize_gui(self):
        self.root=Tk()
        self.root.title('채팅프로그램')
        fr=[]
        for i in range(0,5):
            fr.append(Frame(self.root))
            fr[i].pack(fill=BOTH)

        self.name_label=Label(fr[0], text='사용자이름')
        self.recv_label=Label(fr[1], text='수신메시지:')
        self.send_label=Label(fr[3], text='송신메시지:')
        self.send_btn=Button(fr[3], text='전송', command=self.send_chat)
        self.chat_transcript_area=ScrolledText(fr[2], height=20, width=60)
        self.enter_text_widget=ScrolledText(fr[4], height=5, width=60)
        self.name_widget=Entry(fr[0], width=15)

        self.name_label.pack(side=LEFT)
        self.name_widget.pack(side=LEFT)
        self.recv_label.pack(side=LEFT)
        self.send_btn.pack(side=RIGHT,padx=20)                      # padx:좌우여백
        self.chat_transcript_area.pack(side=LEFT, padx=2, pady=2)   # pady : 상하여백
        self.send_label.pack(side=LEFT)
        self.enter_text_widget.pack(side=LEFT, padx=2, pady=2)

    # message를 전송하는 콜백함수
    # 송신메시지 창에서 메시지를 읽어 수신메시지 창에 표시하고 전송
    def send_chat(self):
        senders_name=self.name_widget.get()+":"
        data=self.enter_text_widget.get(1.0,'end').strip()
        message=(senders_name+data).encode('utf-8')
        self.chat_transcript_area.insert('end',message.decode('utf-8')+'\n')
        self.chat_transcript_area.yview(END) # 수신 창 끝으로 이동
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0,'end')
        return 'break'

    # 데이터 수신 Thread를 생성하고 시작함
    def listen_thread(self):
        t=Thread(target=self.receive_message, args=(self.client_socket,))
        t.daemon=True
        t.start()

    # 소켓에서 메시지를 읽어서 수신메시지 창에 표시
    def receive_message(self,so):
        while True:
            buf = so.recv(256)
            if not buf: # 연결 종료
                break
            self.chat_transcript_area.insert('end',buf.decode('utf-8')+'\n')
            self.chat_transcript_area.yview(END)
        so.close()

if __name__=='__main__':
    ip=input('server IP addr: ')
    if ip =='':
        ip='10.10.21.123'
    port=5010
    ChatClient(ip,port)
    mainloop()


