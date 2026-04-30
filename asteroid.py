import pygame
import random
import math

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS
from logger import log_event 


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.points = self.generate_points()

    def generate_points(self):
        points = []
        num_points = random.randint(8, 12)

        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i

            # random "jaggedness"
            offset = random.uniform(0.7, 1.3)
            r = self.radius * offset

            x = math.cos(angle) * r
            y = math.sin(angle) * r

            points.append((x, y))

        return points

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
        transformed_points = []

        for point in self.points:
            x = int(point[0] + self.position.x)
            y = int(point[1] + self.position.y)
            transformed_points.append((x, y))

        pygame.draw.polygon(
            screen,
            (200, 200, 200),
            transformed_points
        )

        # Optional outline (looks nicer)
        pygame.draw.polygon(
            screen,
            (255, 255, 255),
            transformed_points,
            2
        )

    def update(self, dt):
        self.position += self.velocity * dt