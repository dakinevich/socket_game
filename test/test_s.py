import socket
import time

sock = socket.socket()
sock.bind(("", 5061))
sock.listen(1)
client_sock, addr = sock.accept()
client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
while 1:
    data = client_sock.recv(client_sock.bufsize).decode()
    print(data)
    time.sleep(0.01)
