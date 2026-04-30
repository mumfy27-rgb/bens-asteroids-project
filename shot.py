import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        # skip if not moving
        if self.velocity.length() == 0:
            return

        # direction of the laser
        direction = self.velocity.normalize()

        start_pos = self.position
        end_pos = self.position - direction * 12  # length of laser

        # draw laser beam
        pygame.draw.line(screen, (255, 50, 50), start_pos, end_pos, 3)

    def update(self, dt):
        self.position += self.velocity * dt