# 멀티채팅 서버 프로그램
# threading 모듈을 이용한 TCP 멀티채팅서버 프로그램

from socket import *
from threading import *
import pymysql
import json


class ChatserverMulti:

    # 소켓 생성, 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []  # 접속된 클라이언트 소켓 목록
        self.nickname=[]   # 닉네임 넣기
        self.final_received_message = ''  # 최종 수신 메시지
        self.s_sock = socket(AF_INET, SOCK_STREAM)  # 소켓생성
        self.ip = ''
        self.port = 9028
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 주소 재사용
        self.s_sock.bind((self.ip, self.port))  # 연결대기
        print('클라이언트 대기중...')
        self.s_sock.listen(100)  # 최대 접속인원 3명
        # accept_clinet()를 호출하여 클라이언트와 연결
        self.accept_client()

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터 수신
    def accept_client(self):
        self.list = []
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            print(client)
            if client not in self.clients:  # 만약에 연결클라이언트가 접속된 클라이어트 소켓목록에 없으면
                self.clients.append(client)  # 접속된 소켓을 목록에 추가
            print(f'{ip}:{str(port)}가 연결되었습니다')
            self.list.insert(0, ip)
            self.list.insert(1, port)
            cth = Thread(target=self.receive_message, args=(c_socket,), daemon=True)  # 수신스레드
            cth.start()  # 스레드 시작

    # 데이터를 수신하여 모든 클라이언트에게 전송
    def receive_message(self, c_socket):
        while True:
            try:
                incoming_message = c_socket.recv(2048)
                if not incoming_message:
                    c_socket.close()
                    break
            except Exception as e:
                print(e)
                break
            else:  # 예외가 발생하지 않아 except절을 실행하지 않았을 경우 실행됨.
                self.final_received_message = incoming_message.decode()
                print(self.final_received_message)
                print(bool(self.final_received_message[-3:] == '006'))
                if self.final_received_message == '001':
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chatt', password='0000', db='network')
                    c = conn.cursor()
                    c.execute(f'SELECT send,message FROM network.chat where send not in ("알림")')
                    self.chat_db = c.fetchall()
                    conn.close()
                    aa = json.dumps(self.chat_db)
                    c_socket.send((aa + '001').encode())

                elif self.final_received_message[-3:] == '003':
                    self.send_all_client(c_socket,2)
                    # 접속명단 확인
                    if self.final_received_message[:-3] not in self.nickname:
                        self.nickname.append(self.final_received_message[:-3])
                        print(self.nickname)

                elif self.final_received_message[-3:] == '002':
                    self.send_all_client(c_socket,1)
                    self.db_save()

                elif self.final_received_message[-3:] == '004':
                    self.roomname=self.final_received_message[:-3]

                elif self.final_received_message == '005':
                    self.send_all_client_chat_in(c_socket)

                elif self.final_received_message[-3:] == '006':
                    self.send_all_client(c_socket,5)


    def db_save(self):
        a = self.final_received_message[:-3].split(':')
        conn = pymysql.connect(host='10.10.21.101', port=3306, user='chatt', password='0000', db='network')
        c = conn.cursor()
        c.execute(
            f"insert into `network`.`chat` (send, message, `time`, IP, PORT, roomname) \
            values ('{a[0]}','{a[1]}',{'now()'},'{self.list[0]}','{self.list[1]}','{self.roomname}')")
        conn.commit()
        conn.close()

    # 모든 클라이언트에게 메시지 전송
    def send_all_client(self, sender_socket, num):
        check=['001','002','003','004','005','006']
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            try:
                message=json.dumps(self.final_received_message[:-3])
                self.message_end=message+check[num]
                socket.sendall(self.message_end.encode())
            except:
                self.clients.remove(client)

   # 현재 접속 인원 전체 클라이언트에게 보내기
    def send_all_client_chat_in(self, sender_socket):
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            try:
                message = json.dumps(self.nickname)
                socket.sendall((message +'005').encode())
            except:
                self.clients.remove(client)

if __name__ == '__main__':
    ChatserverMulti()
