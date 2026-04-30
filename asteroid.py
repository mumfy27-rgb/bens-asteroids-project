import pygame
import random

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS
from logger import log_event 

ASTEROID_IMAGES = ["ast1.png", "ast2.png", "ast3.png"]


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

        image_path = random.choice(ASTEROID_IMAGES)
        self.image = pygame.image.load(image_path).convert_alpha()

        # Asteroids get visually bigger the longer the player survives
        survival_seconds = pygame.time.get_ticks() / 1000
        growth_scale = 1 + min(survival_seconds / 120, 1)

        size = int(radius * 2 * growth_scale)

        self.image = pygame.transform.scale(
            self.image,
            (size, size)
        )

    def split(self):
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        
        log_event("asteroid_split")

        random_angle = random.uniform(20, 50)

        velocity_one = self.velocity.rotate(random_angle)
        velocity_two = self.velocity.rotate(-random_angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid_one = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid_two = Asteroid(self.position.x, self.position.y, new_radius)

        asteroid_one.velocity = velocity_one * 1.2
        asteroid_two.velocity = velocity_two * 1.2

    def draw(self, screen):
        rect = self.image.get_rect(center=self.position)
        screen.blit(self.image, rect)

    def update(self, dt):
        self.position += self.velocity * dt