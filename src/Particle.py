import pygame, random

class Particle:
    def __init__(self, x, y, size, direction):
        self.x = x
        self.y = y
        self.color = (255, 255, 255)

        if direction == 'left':
            self.dx = random.uniform(-200, -20)
            self.dy = random.uniform(-200, 200)
        elif direction == 'right':
            self.dx = random.uniform(20, 200)
            self.dy = random.uniform(-200, 200)
        elif direction == 'up':
            self.dx = random.uniform(-200, 200)
            self.dy = random.uniform(-200, -20)
        elif direction == 'down':
            self.dx = random.uniform(-200, 200)
            self.dy = random.uniform(20, 200)

        if size == 'normal':
            self.size = random.randint(10, 20)
            self.lifetime = random.uniform(0.1, 0.2)
        elif size == 'big':
            self.size = random.randint(15, 30)
            self.lifetime = random.uniform(0.175, 0.35)
            self.dx *= 2
            self.dy *= 2

    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.size = self.size - (self.size / self.lifetime) * dt

    def render(self, screen):
        if self.size > 0:
            pygame.draw.rect(screen, self.color, pygame.Rect(int(self.x), int(self.y), int(self.size), int(self.size)))
