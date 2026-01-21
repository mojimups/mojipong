import pygame
from constant import *

class Ball:
    def __init__(self, screen, x, y, width, height):
        self.screen=screen
        self.rect = pygame.Rect(x, y, width, height)
        self.dx = 0
        self.dy = 0
        
    def Collides(self, paddle):
        # first, check to see if the left edge of either is farther to the right than the right edge of the other
        if self.rect.x > paddle.rect.x + paddle.rect.width or paddle.rect.x > self.rect.x + self.rect.width:
            return False
        # then check to see if the bottom edge of either is higher than the top edge of the other
        if self.rect.y > paddle.rect.y + paddle.rect.height or paddle.rect.y > self.rect.y + self.rect.height:
            return False
        return True

    def ContinuousCollisionDetect(self, dt, paddle):
        steps = COLLISION_CHECK_STEPS
        for i in range(1, steps):
            if self.rect.move(self.dx * dt * i/steps, self.dy * dt * i/steps).colliderect(paddle.rect):
                return True, i
        return False, None

    def Reset(self):
        self.rect.x = WIDTH / 2 - 6
        self.rect.y = HEIGHT / 2 - 6
        self.dx = 0
        self.dy = 0

    def Hide(self):
        self.rect.x = -10000

    def update(self, dt):
        self.rect.x += self.dx * dt
        self.rect.y += self.dy * dt

    def render(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect)
