import socket
import time

sock = socket.socket()
sock.connect(("localhost", 5061))
time.sleep(1)

for i in range(1000):
    sock.send(f"{i}Sd asd s d".encode())