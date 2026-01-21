import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from constant import *
from GameMain import GameMain

if __name__ == '__main__':
    main = GameMain()
    clock = pygame.time.Clock()
    
    while True:
        pygame.display.set_caption("MojiPong ({:d} FPS)".format(int(clock.get_fps()))) 

        # elapsed time from the last call
        dt = clock.tick(MAX_FRAME_RATE)/1000.0

        events = pygame.event.get()
        main.update(dt, events)
        main.render()
        pygame.display.update()
