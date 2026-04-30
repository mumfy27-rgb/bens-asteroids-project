import pygame

from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0

        # 🚀 Load spaceship image
        self.image = pygame.image.load("ship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))

    def shoot(self):
        if self.shoot_timer > 0:
            return

        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED

        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt):
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)

        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self, dt):
        direction = pygame.Vector2(0, -1).rotate(self.rotation)
        self.position += direction * PLAYER_SPEED * dt

    def draw(self, screen):
        # 🔄 Rotate and draw the ship
        rotated_image = pygame.transform.rotate(self.image, -self.rotation)
        rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rect)