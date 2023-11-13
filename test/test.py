import threading
import pygame


def t1():
    pygame.init()
    screen = pygame.display.set_mode([500, 500])
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        screen.fill((5, 5, 5))
        pygame.draw.circle(screen, (255, 255, 255), pygame.mouse.get_pos(), 3)
        pygame.display.flip()

    pygame.quit()


def t2():
    #print("d")
    pass
        

tt1 = threading.Thread(target=t1, daemon=True)
tt2 = threading.Thread(target=t2, daemon=True)

tt1.start()
tt2.start()

tt2.join()
tt1.join()


