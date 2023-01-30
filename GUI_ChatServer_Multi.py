# 멀티채팅 서버 프로그램
# threading 모듈을 이용한 TCP 멀티채팅서버 프로그램

from socket import *
from threading import *
import pymysql

class ChatserverMulti:

    # 소켓 생성, 연결되면 accept_client() 호출
    def __init__(self):
        self.clients=[]               # 접속된 클라이언트 소켓 목록
        self.final_received_message='' # 최종 수신 메시지
        self.s_sock=socket(AF_INET,SOCK_STREAM)           # 소켓생성
        self.ip=''
        self.port=9523
        self.s_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) # 주소 재사용
        self.s_sock.bind((self.ip,self.port))             # 연결대기
        print('클라이언트 대기중...')
        self.s_sock.listen(3)                             # 최대 접속인원 3명
        # accept_clinet()를 호출하여 클라이언트와 연결
        self.accept_client()

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터 수신
    def accept_client(self):
        self.list=[]
        while True:
            client=c_socket,(ip,port)=self.s_sock.accept()
            print(client)
            if client not in self.clients:      # 만약에 연결클라이언트가 접속된 클라이어트 소켓목록에 없으면
                self.clients.append(client)     # 접속된 소켓을 목록에 추가
            print(f'{ip}:{str(port)}가 연결되었습니다')
            self.list.insert(0,ip)
            self.list.insert(1,port)
            cth=Thread(target=self.receive_message, args=(c_socket,), daemon=True)    # 수신스레드
            cth.start()    # 스레드 시작

    # 데이터를 수신하여 모든 클라이언트에게 전송
    def receive_message(self,c_socket):
        while True:
            try:
                incoming_message=c_socket.recv(256)
                if not incoming_message: # 연결이 종료됨
                    break
            except:
                continue
            else: # 예외가 발생하지 않아 except절을 실행하지 않았을 경우 실행됨.
                self.final_received_message=incoming_message.decode('utf-8')
                print(self.final_received_message)
                self.send_all_client(c_socket)
                self.db_save()
        # c_socket.close()
    def db_save(self):
        a = self.final_received_message.split(':')
        print(type(a[0]), a[0])
        print(type(a[1]), a[1])
        print(self.list[0])
        print(self.list[1])
        conn = pymysql.connect(host='10.10.21.101', port=3306, user='chatt', password='0000', db='network')
        c = conn.cursor()
        c.execute(f"insert into `network`.`chat` (send, message, `time`, IP, PORT) values ('{a[0]}','{a[1]}',{'now()'},'{self.list[0]}','{self.list[1]}')")
        conn.commit()
        conn.close()

    # 모든 클라이언트에게 메시지 전송
    def send_all_client(self,senders_socket):
        for client in self.clients:             # 목록에 있는 모든 소켓에 대해
            socket, (ip,port) = client
            # if socket is not senders_socket:    # 송신 클라이언트 제외
            try:
                socket.sendall(self.final_received_message.encode())
            except: # 연결종료
                self.clients.remove(client) # 소켓 제거
                print(f'{ip}:{port} 연결이 종료되었습니다')

if __name__=='__main__':
    ChatserverMulti()