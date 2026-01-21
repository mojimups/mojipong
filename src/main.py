import pygame, sys, random, time, numpy
import pygame.sndarray
import asyncio
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from constant import *
from GameMain import GameMain

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

async def main():
    game = GameMain()
    
    while True:
        # pygame.display.set_caption("MojiPong ({:d} FPS)".format(int(clock.get_fps()))) 
        pygame.display.set_caption("MojiPong") 

        # elapsed time from the last call
        pygame.display.update()
        await asyncio.sleep(0)  # Yield control to browser

        dt = clock.tick(MAX_FRAME_RATE)/1000.0

        events = pygame.event.get()
        game.update(dt, events)
        game.render()

asyncio.run(main())
