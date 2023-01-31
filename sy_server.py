# threading 모듈을 이용한 TCP 멀티 채팅 서버 프로그램

import json
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
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 주소 재사용
        self.s_sock.bind((self.ip, self.port))    # 연결 대기
        print("클라이언트 대기 중...")
        self.s_sock.listen(100)   # 최대 접속인원 100명
        self.accept_client()    # 클라이언트와 연결

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        self.add = []
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)   # 접속된 소켓을 목록에 추가
            print(ip, ':', str(port), ' 가 연결되었습니다')
            print(self.clients)
            self.add.insert(0, ip)
            self.add.insert(1, port)
            cth = Thread(target=self.receive_messages, args=(c_socket,), daemon=True)  # 수신 스레드
            cth.start()   # 스레드 시작

    # 데이터를 수신하여 모든 클라이언트에게 전송한다
    def receive_messages(self, c_socket):
        # now = datetime.now()
        # now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        # print(now_time)
        while True:
            try:
                incoming_message = c_socket.recv(1024)
                if not incoming_message: # 연결이 종료됨
                    break
            except:
                continue
            else:  # 예외가 발생하지 않아 except 실행되지 않을시 실행
                self.final_received_message = incoming_message.decode('utf-8')
                print(self.final_received_message)
                # self.final_received_message = json.loads(incoming_message.decode('utf-8'))
                # json.dumps(self.final_received_message)
                print(self.final_received_message)
                # ---------------------------------------------------------------------------
                if self.final_received_message[-3:] == '001':
                    self.m = self.final_received_message.split(':')
                    print(type(self.m[0]), self.m[0])
                    print(type(self.m[1]), self.m[1])
                    print(self.add[0])
                    print(self.add[1])
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
                    cursor = conn.cursor()
                    cursor.execute(
                        f"INSERT INTO chat (send, message, time, IP, PORT) VALUES('{self.m[0]}','{self.m[1]}',{'now()'},'{self.add[0]}','{self.add[1]}')")
                    conn.commit()
                self.send_all_clients(c_socket)
        c_socket.close()

    # 송신 클라이언트를 제외한 모든 클라이언트에게 메시지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket: # 송신 클라이언트는 제외
                try:
                    if self.final_received_message[-3:] == '001':
                        socket.sendall((self.final_received_message).encode('utf-8'))
                except:  # 연결 종료
                    self.clients.remove(client)   # 소켓 제거
                    print("{}, {} 연결이 종료되었습니다".format(ip, port))
            else:
                if self.final_received_message[-3:] == '002':
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
                    cursor = conn.cursor()
                    cursor.execute(
                        f"SELECT send, message FROM chat")
                    self.chattext = cursor.fetchall()
                    print(self.chattext)
                    conn.close()
                    chattext = json.dumps(self.chattext)
                    print(chattext)
                    senders_socket.sendall((chattext + '002').encode())


if __name__ == "__main__":
    MultiChatServer()
