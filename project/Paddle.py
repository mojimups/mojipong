import pygame
from constant import *

class Paddle:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen

        self.rect = pygame.Rect(x, y, width, height)
        self.dy = 0

    def update(self, dt):
        if self.dy > 0:
            if self.rect.y + self.rect.height < HEIGHT:
                self.rect.y += self.dy*dt
        else:
            if self.rect.y >= 0:
                self.rect.y += self.dy*dt

    def render(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect)