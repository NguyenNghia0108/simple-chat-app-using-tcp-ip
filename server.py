import socket
import threading

host = socket.gethostbyname("127.0.0.1")
port = 2207

server_socket = socket.socket()
server_socket.bind((host,port))
server_socket.listen(500)

clients = []
nicknames = []


def broadcast(message):
    nicknames_list = '\n'.join(nicknames)
    for client in clients:
        client.send(message)
        client.send(f'[USERS]{nicknames_list}'.encode("utf-8"))


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            # print(f"{nicknames[clients.index(client)]} сказал: {message.decode('utf-8')}")
            broadcast(message)
        except:
            index = clients.index(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            clients.remove(client)
            client.close()
            broadcast(f"{nickname} đã rời khỏi máy chủ!\n".encode("utf-8"))
            break


def receive():
    while True:
        client, address = server_socket.accept()
        print(f"Kết nối với {str(address)}")

        client.send("NICK".encode("utf-8"))
        nickname = client.recv(1000).decode("utf-8")

        nicknames.append(nickname)
        clients.append(client)

        print(f"Tên người dùng: {nickname}")
        broadcast(f"{nickname} đã kết nối với máy chủ!\n".encode("utf-8"))

        thread = threading.Thread(target=handle, args=(client, ))
        thread.start()

if __name__ == '__main__':
    print("Server is running...")
    receive()
