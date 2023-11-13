import threading
import socket
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import queue

sleep_time = 0.001

def recv_all(connection):
    data = b''
    while 1:
        msg = connection.recv(1024)
        data+=msg
        if len(msg) != 1024:
            return data


class Client():
    def __init__(self, socket):
        self.c_socket = socket
        self.pos = [0, 0]
        self.index = socket.fileno()
        
    def send(self, s):
        self.c_socket.send(str(s).encode())

    def wait_msg(self, t=0):
        self.c_socket.settimeout(t)
        return recv_all(self.c_socket).decode()
    
    def update(self, p):
        self.pos = p.pos
    
class Player():
    def __init__(self, pos = [0, 0], index = -1):
        self.pos = pos
        self.index = index

    @classmethod
    def fromclient(cls, c: Client):
        return cls(c.pos, c.index)

    @classmethod
    def fromstr(cls, s):
        s = s.split(" ")
        pos = [int(s[1]), int(s[2])]
        index = int(s[0])
        return cls(pos, index)


    def blit(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, 3)

    def serialize(self):
        return f"{self.index} {self.pos[0]} {self.pos[1]}"



def game_thread():
    global CLIENTS_LIST
    global running
    pygame.init()
    screen = pygame.display.set_mode([500, 500], flags=pygame.RESIZABLE)
    pygame.display.set_icon(pygame.Surface([0, 0]))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((5, 5, 5))

        #POS = pygame.mouse.get_pos()
        for player in CLIENTS_LIST:
            pygame.draw.circle(screen, (255, 255, 255), player.pos, 3)
        #pygame.draw.circle(screen, (255, 255, 255), pygame.mouse.get_pos(), 3)
        
        pygame.display.flip()
        time.sleep(sleep_time)

    pygame.quit()

def accept_loop():
    while True:
        time.sleep(sleep_time)
        try:
            host_sock.listen(1)
            client_sock, addr = host_sock.accept()
            new_client = Client(client_sock)
            print(f"client {new_client.index} has been connected")

            new_client.send(str(new_client.index)+';')
            CLIENTS_LIST.append(new_client)
        except Exception as e:
            print(1, e)
            break



def netdata_listener():
    global CLIENTS_LIST
    while True:
        local_clients = CLIENTS_LIST
        time.sleep(sleep_time)
        for client in local_clients:
            try:
                messange = client.wait_msg(1)

                client_player = Player.fromstr(messange)
                for i in range(len(CLIENTS_LIST)):
                    if CLIENTS_LIST[i].index == client.index:
                        CLIENTS_LIST[i].update(client_player)
            except Exception as e:
                print(2, e)
                for i in range(len(CLIENTS_LIST)):
                    if CLIENTS_LIST[i].index == client.index:
                        CLIENTS_LIST.pop(i)
                        print(f"client {client.index} has been disconnected")
                        break
def netdata_sender():
    global CLIENTS_LIST
    while True:
        local_clients = CLIENTS_LIST
        time.sleep(sleep_time) # server render starts faster
        for client in local_clients:
            try:
                messange = ','.join([Player.fromclient(i).serialize() for i in local_clients])
                client.send(messange+'; ')
                
            except Exception as e:
                print(3, e)



HOST = ""
PORT = 5060
running = True


print(f"\nHOST: {HOST}\nPORT: {PORT}")

host_sock = socket.socket()
CLIENTS_LIST = []
try:
    host_sock.bind((HOST, PORT))
except:
    print("PORT IS ALREADY BUSY")
    exit()
print("SERVER\n")
pygame.display.set_caption('server')

thread_game = threading.Thread(target=game_thread, daemon=True)
thread_listener = threading.Thread(target=netdata_listener, daemon=True)
thread_sender = threading.Thread(target=netdata_sender, daemon=True)
thread_accept = threading.Thread(target=accept_loop, daemon=True)

thread_game.start()
thread_accept.start()
thread_listener.start()
thread_sender.start()

thread_game.join()
host_sock.close()
print("\nDISCONNECTED")


