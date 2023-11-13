import threading
import multiprocessing
import socket
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

sleep_time = 0.001

def recv_all(connection):
    data = b''
    while 1:
        msg = connection.recv(1024)
        data+=msg
        if len(msg) != 1024:
            return data

class Client():
    pass


class Player():
    def __init__(self, pos:list[int, int] = [0, 0], index:int = -1):
        self.pos = pos
        self.index = index

    @classmethod
    def fromclient(cls, c: Client):
        return cls(c.pos, c.index)

    @classmethod
    def fromstr(cls, s: str):
        s = s.split(" ")
        pos = [int(s[1]), int(s[2])]
        index = int(s[0])
        return cls(pos, index)


    def blit(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, 3)

    def serialize(self):
        return f"{self.index} {self.pos[0]} {self.pos[1]}"





def game_thread():
    global running
    global CLIENTPLAYER
    global PLAYERS
    pygame.init()
    screen = pygame.display.set_mode([500, 500])
    pygame.display.set_icon(pygame.Surface([0, 0]))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((5, 5, 5))

        CLIENTPLAYER.pos = pygame.mouse.get_pos()
        #CLIENTPLAYER.pos = [int(time.time()%100), int(time.time()%115)]
        for player in PLAYERS:
            player.blit(screen)
            
        pygame.display.flip()
        time.sleep(sleep_time)

    pygame.quit()



def netdata_listener():
    global CLIENTPLAYER
    global PLAYERS
    global running
    global client_sock
    while True:
        time.sleep(sleep_time)
        try:
            client_sock.settimeout(10)
            messange = recv_all(client_sock).decode()
            #print("got msg", messange)
            players_data = messange.split(";")[0]
            players_data = players_data.split(",")
            PLAYERS_t = []

            for p in players_data:
                if p:
                    PLAYERS_t.append(Player.fromstr(p))
            PLAYERS = PLAYERS_t

        except Exception as e:
            print("DISCONNECTED 1", e)
            running = False
            break
def netdata_sender():
    global CLIENTPLAYER
    global PLAYERS
    global running
    global client_sock

    while True:
        time.sleep(sleep_time)
        try:
            messange = (CLIENTPLAYER.serialize()+' ')
            #print("send msg", messange)
            client_sock.send(messange.encode())

        except Exception as e:
            print("DISCONNECTED 2", e)
            running = False
            break


HOST = "localhost" # localhost / 91.77.161.19
PORT = 5060
PLAYERS = []
running = True

if HOST == "localhost":
    print("LOCAL MODE")
print(f"\nHOST: {HOST}\nPORT: {PORT}")

client_sock = socket.socket()
try:
    client_sock.settimeout(1)
    client_sock.connect((HOST, PORT))
    index = client_sock.recv(1024).decode()
    index = int(index.split(';')[0])
    CLIENTPLAYER = Player([10,11], index)


    print(f"CONNECTED\nCLIENT INDEX: {index}\n")
    pygame.display.set_caption(f'client {index}')

    thread_listener = threading.Thread(target=netdata_listener, daemon=True)
    thread_sender = threading.Thread(target=netdata_sender, daemon=True)
    thread_game = threading.Thread(target=game_thread, daemon=True)

    thread_game.start()
    thread_sender.start()
    thread_listener.start()


    thread_game.join()

except:
    print("\n!Server not found")

client_sock.close()

