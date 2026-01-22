import pygame
from constant import *

class Paddle:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen

        self.rect = pygame.Rect(x, y, width, height)
        self.dy = 0

    def update(self, dt):
        self.rect.y += self.dy * dt
        
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y + self.rect.height > HEIGHT:
            self.rect.y = HEIGHT - self.rect.height

    def render(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect)