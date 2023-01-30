# threading 모듈을 이용한 TCP 멀티 채팅 서버 프로그램

import pymysql
from socket import *
from threading import *
from datetime import datetime

class MultiChatServer:
    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []  # 접속된 클라이언트 소켓 목록
        self.final_received_message = ""  # 최종 수신 메시지
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.ip ='10.10.21.101'
        self.port = 9180
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print("클라이언트 대기 중...")
        self.s_sock.listen(100)
        self.accept_client()

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)   # 접속된 소켓을 목록에 추가
            print(ip, ':', str(port), ' 가 연결되었습니다')
            print(self.clients)
            cth = Thread(target=self.receive_messages, args=(c_socket,))  # 수신 스레드
            cth.start()   # 스레드 시작
            # list = []
            # list.append(0, ip)
            # list.append(1, str(port))

    # 데이터를 수신하여 모든 클라이언트에게 전송한다
    def receive_messages(self, c_socket):
        now = datetime.now()
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        print(now_time)
        while True:
            try:
                incoming_message = c_socket.recv(256)
                if not incoming_message: # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_received_message = incoming_message.decode('utf-8')
                print(self.final_received_message)
                self.send_all_clients(c_socket)
            # a = self.final_received_message.split(':')
            # print(a)
            # print(type(a[0]), a[0])
            # print(type(a[1]), a[1])
            # print(self.list[0])
            # print(self.list[1])
            # conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
            # c = conn.cursor()
            # c.execute(
            #     f"INSERT INTO chat (send, message, time, IP, PORT) VALUES('{a[0]}','{a[1]}',{'now()'},'{self.list[0]}','{self.list[1]}')")
            # conn.commit()
            # conn.close()

    # 송신 클라이언트를 제외한 모든 클라이언트에게 메시지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients: # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket: # 송신 클라이언트는 제외
                try:
                    socket.sendall(self.final_received_message.encode('utf-8'))
                except:  # 연결 종료
                    self.clients.remove(client)   # 소켓 제거
                    print("{}, {} 연결이 종료되었습니다".format(ip, port))


if __name__ == "__main__":
    MultiChatServer()
