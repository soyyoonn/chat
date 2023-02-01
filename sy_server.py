# threading 모듈을 이용한 TCP 멀티 채팅 서버 프로그램

import json
import pymysql
from socket import *
from threading import *
from datetime import datetime

class MultiChatServer:
    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []   # 접속된 클라이언트 소켓 목록을 넣을 리스트
        self.final_received_message = ""  # 최종 수신 메시지
        self.s_sock = socket(AF_INET, SOCK_STREAM)  # 서버 소켓 생성
        self.ip ='10.10.21.101'
        self.port = 9180
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 주소 재사용
        self.s_sock.bind((self.ip, self.port))    # 연결 대기
        print("클라이언트 대기 중...")
        self.s_sock.listen(100)   # 최대 접속인원 100명
        self.accept_client()    # 클라이언트와 연결

    # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self):
        self.add = []   # 아이피와 포트 넣을 리스트
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)   # 접속된 소켓을 목록에 추가
            print(ip, ':', str(port), ' 가 연결되었습니다')
            print(self.clients)
            self.add.insert(0, ip)   # 리스트 0번째에 아이피 추가
            self.add.insert(1, port)  # 리스트 1번째에 포트 추가
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
                if not incoming_message:  # 연결이 종료됨
                    break
            except:
                continue
            else:  # 예외가 발생하지 않아 except 실행되지 않을시 실행
                self.final_received_message = incoming_message.decode('utf-8')  # 클라이언트 소켓에서 받아 온 메시지
                print(self.final_received_message)
                # ---------------------------------------------------------------------------
                if self.final_received_message[-3:] == '001':
                    self.m = self.final_received_message.split(':')
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
                    cursor = conn.cursor()
                    # DB에 데이터 저장
                    cursor.execute(
                        f"INSERT INTO chat (send, message, time, IP, PORT, roomname) VALUES('{self.m[0]}','{self.m[1]}',{'now()'},'{self.add[0]}','{self.add[1]}','{self.m[2]}')")
                    conn.commit()
                self.send_all_clients(c_socket)  # 열려 있는 모든 클라이언트들에게 메시지 보내기
        c_socket.close()

    # 송신 클라이언트를 제외한 모든 클라이언트에게 메시지 전송
    def send_all_clients(self, senders_socket):
        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket: # 송신 클라이언트는 제외
                try:
                    if self.final_received_message[-3:] == '001':  # 받은 메시지 마지막 3글자가 001일때
                        socket.sendall((self.final_received_message).encode('utf-8')) # 메시지 전송
                except:  # 연결 종료
                    self.clients.remove(client)   # 소켓 제거
                    print(f"{ip}, {port} 연결이 종료되었습니다")
            else:
                if self.final_received_message[-3:] == '002':  # 받은 메시지 마지막 3글자가 002 일때
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
                    cursor = conn.cursor()
                    # DB에 저장된 채팅방 목록 데이터 불러오기
                    cursor.execute(f"SELECT roomname FROM room")
                    self.chatroom = cursor.fetchall()
                    print(self.chatroom)
                    conn.close()
                    chatroom = json.dumps(self.chatroom)
                    print(chatroom)
                    senders_socket.sendall((chatroom + '002').encode('utf-8'))

                elif self.final_received_message[-3:] == '003':  # 받은 메시지 마지막 3글자가 003 일때
                    room = self.final_received_message.split(':')[0]
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
                    cursor = conn.cursor()
                    # DB에 저장된 메시지 데이터 불러오기
                    cursor.execute(
                        f"SELECT send, message FROM chat WHERE roomname = '{room}'")
                    self.chattext = cursor.fetchall()
                    print(self.chattext)
                    conn.close()
                    chattext = json.dumps(self.chattext)  # json 사용해서 리스트로 변환
                    print(chattext)
                    senders_socket.sendall((chattext + '003').encode('utf-8'))  # 메시지 전송

                elif self.final_received_message[-3:] == '004':  # 채팅방 생성
                    room = self.final_received_message.split(':')[0]
                    conn = pymysql.connect(host='10.10.21.101', port=3306, user='chat', password='0000', db='network')
                    cursor = conn.cursor()
                    # DB에 저장된 데이터 불러오기
                    cursor.execute(
                        f"INSERT INTO room (roomname) VALUES('{room}')")
                    conn.commit()
                    conn.close()
                    print('이게들어가야돼',room)
                    senders_socket.sendall((room + '004').encode('utf-8'))

if __name__ == "__main__":
    MultiChatServer()
